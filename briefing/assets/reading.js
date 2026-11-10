/* Visible time is foreground exposure, not a claim about a person's attention.
   Embedded in each brief. No imports, requests except the explicit local save adapter. */
(function(root){
  'use strict';
  function clone(value){return JSON.parse(JSON.stringify(value));}
  function Clock(identity,targets){
    this.value=Object.assign({},identity,{targets:targets.map(function(t){return Object.assign({},t,{visible_ms:null});}),gaps:[]});
    this.last=null;this.started=false;this.fractions={};this.sequence=0;this.openGap=null;
  }
  Clock.prototype.sample=function(now,activity,visible,eligible){
    if(!Number.isFinite(now)||now<0)throw new Error('Invalid monotonic sample');
    var previous=this.last,delta=previous?now-previous.at:0,self=this;
    if(delta<0)throw new Error('Monotonic clock moved backwards');
    var reason=delta>3000?'clock_gap':previous&&previous.activity==='unknown'?'activity_unknown':null;
    if(previous&&reason){
      if(this.openGap&&this.openGap.reason===reason)this.openGap.elapsed_ms+=Math.floor(delta);
      else{this.openGap={sequence:++this.sequence,reason:reason,elapsed_ms:Math.floor(delta)};this.value.gaps.push(this.openGap);}
    }else{
      this.openGap=null;
      if(previous&&previous.activity==='active')this.value.targets.forEach(function(t){
        if(t.visible_ms===null||!previous.visible.has(t.anchor))return;
        var elapsed=delta+(self.fractions[t.anchor]||0),whole=Math.floor(elapsed);
        self.fractions[t.anchor]=elapsed-whole;t.visible_ms+=whole;
      });
    }
    if(activity==='active'){
      this.started=true;
      this.value.targets.forEach(function(t){if((eligible||[]).includes(t.anchor)&&t.visible_ms===null)t.visible_ms=0;});
    }
    this.last={at:now,activity:activity,visible:new Set(visible)};
  };
  Clock.prototype.checkpoint=function(){return this.started?clone(this.value):null;};
  root.BriefReadingClock=Clock;
  if(typeof document==='undefined')return;

  function title(el){var node=el.cloneNode(true);node.querySelectorAll('.note-btn,.concur-zone,[data-reader-ui]').forEach(function(n){n.remove();});var label=node.querySelector(':scope > .lbl,h1,h3,h4');return (label||node).textContent.replace(/\s+/g,' ').trim().slice(0,500);}
  function targets(){
    return Array.from(document.querySelectorAll('[data-brief-anchor]')).filter(function(el){return !el.closest('dialog,nav,#last-time,.last-time-strip');}).map(function(el){
      var section=el.closest('section'),heading=section&&section.querySelector('h2[data-brief-anchor]');
      var kind=el.matches('.opening,.lede,h1')?'opening':el.tagName==='H2'?'section':el.tagName==='FIGURE'?'figure':'entry';
      return {el:el,box:kind==='section'&&section?section:el,anchor:el.dataset.briefAnchor,title:title(el),kind:kind,parent:kind!=='section'&&heading&&heading!==el?heading.dataset.briefAnchor:null};
    });
  }
  function noteDiff(before,after){
    var edits=[],keys=new Set(Object.keys(before.notes).concat(Object.keys(after.notes))),same=function(a,b){return JSON.stringify(a)===JSON.stringify(b);};
    keys.forEach(function(anchor){
      var a=before.notes[anchor]||[],b=after.notes[anchor]||[];
      a.forEach(function(n){if(!b.some(function(m){return same(n,m);}))edits.push({op:'delete',anchor:anchor,note:n});});
      b.forEach(function(n){if(!a.some(function(m){return same(n,m);}))edits.push({op:'add',anchor:anchor,note:n});});
    });
    new Set(Object.keys(before.concurs).concat(Object.keys(after.concurs))).forEach(function(anchor){
      var a=before.concurs[anchor]||null,b=after.concurs[anchor]||null;if(a!==b)edits.push({op:'concur',anchor:anchor,before:a,value:b});
    });return edits;
  }
  function init(){
    var metaNode=document.getElementById('brief-meta'),island=document.getElementById('report-reading');if(!metaNode||!island)return;
    var meta,record;try{meta=JSON.parse(metaNode.textContent);record=JSON.parse(island.textContent);}catch(e){return;}
    var cfg=root.BRIEF_REVIEW,host=root.BRIEF_READING_HOST;
    var enabled=host&&typeof host.recording==='boolean'?host.recording:!navigator.webdriver;
    var list=targets(),identity={session:crypto.randomUUID(),document:meta.id,revision:meta.revision,host:'browser',method:1};
    var clock=new Clock(identity,list.map(function(t){return {anchor:t.anchor,title:t.title,kind:t.kind,parent:t.parent};}));
    var storageKey='brief-reading:'+meta.id+':'+meta.revision+':';
    var pending=[],busy=false,savedSignature=null,statusText=cfg?'Local review ready':'Browser storage only';
    var baseline={notes:JSON.parse(document.getElementById('report-notes').textContent),concurs:JSON.parse(document.getElementById('report-concurs').textContent)};
    try{for(var i=0;i<localStorage.length;i++){var key=localStorage.key(i);if(!key.startsWith(storageKey))continue;var held=JSON.parse(localStorage.getItem(key));if(held&&held.reading&&held.reading.document===meta.id&&held.reading.revision===meta.revision)pending.push(held);}}catch(e){statusText='Pending · browser recovery storage unavailable';}
    var nav=document.querySelector('nav.sections'),labels=new Map();
    if(nav){
      nav.dataset.readerUi='';nav.replaceChildren();
      list.filter(function(t){return t.kind==='section'||t.kind==='figure'||t.kind==='entry';}).forEach(function(t){
        var a=document.createElement('a');a.href='#'+t.anchor;a.dataset.readingAnchor=t.anchor;
        if(t.parent)a.className='reading-child';
        var name=document.createElement('span');name.className='reading-label';name.textContent=t.title.length>45?t.title.slice(0,43)+'…':t.title;
        var time=document.createElement('span');time.className='reading-time';time.textContent='—';time.setAttribute('aria-label','Visible time');a.append(name,time);nav.append(a);labels.set(t.anchor,{link:a,time:time});
      });document.body.append(nav);document.documentElement.classList.add('has-reading-rail');
    }
    var status=document.querySelector('.notes-persistence');
    function currentNotes(){return root.BriefNotes?root.BriefNotes.snapshot():clone(baseline);}
    function activity(){
      if(!enabled)return 'inactive';
      if(typeof document.hasFocus!=='function')return 'unknown';
      return document.visibilityState==='visible'&&document.hasFocus()&&!document.querySelector('dialog[open]')?'active':'inactive';
    }
    function geometry(){
      var visible=[],eligible=[],top=0,bottom=innerHeight;
      if(nav&&innerWidth<1100)top=nav.getBoundingClientRect().bottom;
      var bar=document.getElementById('notebar');if(bar)bottom=Math.min(bottom,bar.getBoundingClientRect().top);
      list.forEach(function(t){
        if(t.box.closest('[hidden],dialog:not([open])'))return;
        var r=t.box.getBoundingClientRect();if(r.width<=0||r.height<=0)return;eligible.push(t.anchor);
        if(r.bottom>top&&r.top<bottom&&r.right>0&&r.left<innerWidth)visible.push(t.anchor);
      });return {visible:visible,eligible:eligible};
    }
    function sample(){var g=geometry();clock.sample(performance.now(),activity(),g.visible,g.eligible);return g;}
    function combined(){
      var sessions=record.sessions.slice(),latest=new Map();pending.forEach(function(p){latest.set(p.reading.session,p.reading);});
      var now=clock.checkpoint();if(now)latest.set(now.session,now);
      latest.forEach(function(s,id){var index=sessions.findIndex(function(v){return v.session===id;});if(index<0)sessions.push(s);else sessions[index]=s;});
      return {format:1,sessions:sessions};
    }
    function times(){
      var result=new Map();combined().sessions.filter(function(s){return s.revision===meta.revision;}).forEach(function(s){s.targets.forEach(function(t){if(t.visible_ms!==null)result.set(t.anchor,(result.get(t.anchor)||0)+t.visible_ms);});});return result;
    }
    function formatted(ms){var seconds=Math.floor(ms/1000);return Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0');}
    var lastActive=null;
    function paint(){
      var map=times(),visible=geometry().visible,active=list.find(function(t){return t.kind==='section'&&visible.includes(t.anchor);});
      labels.forEach(function(v,key){v.time.textContent=map.has(key)?formatted(map.get(key)):'—';if(active&&key===active.anchor)v.link.setAttribute('aria-current','location');else v.link.removeAttribute('aria-current');});
      if(active&&active.anchor!==lastActive&&nav){var item=labels.get(active.anchor);if(item&&innerWidth>=1100){var link=item.link;if(link.offsetTop<nav.scrollTop)nav.scrollTop=link.offsetTop;else if(link.offsetTop+link.offsetHeight>nav.scrollTop+nav.clientHeight)nav.scrollTop=link.offsetTop+link.offsetHeight-nav.clientHeight;}lastActive=active.anchor;}
      if(status)status.textContent=statusText;
      var exportButton=document.getElementById('btn-export');if(exportButton&&combined().sessions.some(function(s){return s.revision===meta.revision;}))exportButton.disabled=false;
    }
    function persist(){try{var own=pending.find(function(p){return p.reading.session===clock.value.session;});if(own)localStorage.setItem(storageKey+clock.value.session,JSON.stringify(own));}catch(e){statusText='Pending · browser recovery storage unavailable';}}
    function enqueue(){
      if(!enabled)return;sample();var reading=clock.checkpoint();if(!reading)return;
      var next={format:1,reading:reading,note_edits:noteDiff(baseline,currentNotes())};
      var signature=JSON.stringify(next);if(signature===savedSignature)return;
      var index=pending.findIndex(function(p){return p.reading.session===reading.session;});if(index<0)pending.push(next);else pending[index]=next;
      statusText=cfg?'Pending · saving original HTML':'Browser storage only · original HTML not saved';persist();paint();
    }
    async function flush(){
      if(!enabled||!cfg||busy||!pending.length)return;busy=true;
      var next=clone(pending[0]),notesAtSend=currentNotes();
      if(next.reading.session===clock.value.session){next.note_edits=noteDiff(baseline,notesAtSend);pending[0]=clone(next);persist();}
      try{
        var response=await fetch(cfg.save,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(next),keepalive:JSON.stringify(next).length<60000});
        var result=await response.json();if(!response.ok||result.state!=='saved')throw new Error(result.reason||'Save was not acknowledged');
        var index=record.sessions.findIndex(function(s){return s.session===result.acknowledged.session;});if(index<0)record.sessions.push(result.acknowledged);else record.sessions[index]=result.acknowledged;
        var current=pending.findIndex(function(p){return p.reading.session===next.reading.session;});
        if(current>=0&&JSON.stringify(pending[current])===JSON.stringify(next))pending.splice(current,1);
        try{var key=storageKey+next.reading.session;if(localStorage.getItem(key)===JSON.stringify(next))localStorage.removeItem(key);}catch(e){statusText='Saved · recovery storage could not be cleared';}
        if(next.reading.session===clock.value.session){baseline=notesAtSend;savedSignature=JSON.stringify(next);}
        statusText=pending.length?'Pending · newer changes wait':'Saved to original HTML';persist();
      }catch(e){statusText='Pending · '+e.message;}finally{busy=false;paint();}
    }
    function changed(){sample();paint();if(activity()!=='active'){enqueue();flush();}}
    root.BriefReading={enabled:enabled,record:combined,checkpoint:function(){enqueue();return flush();},
      describe:function(){return list.map(function(t){var r=t.box.getBoundingClientRect();return {anchor:t.anchor,title:t.title,kind:t.kind,parent:t.parent,rect:r.width>0&&r.height>0?{x:r.x+scrollX,y:r.y+scrollY,w:r.width,h:r.height}:null};});},
      summary:function(){var map=times();if(!map.size)return '';return '\nVISIBLE TIME — '+meta.id+' · '+meta.revision.slice(7,19)+'\nRecorded foreground exposure across sessions; overlapping targets are not additive.\n'+list.map(function(t){return '['+t.anchor+'] '+t.title+' · '+(map.has(t.anchor)?formatted(map.get(t.anchor)):'unknown')+' visible';}).join('\n')+'\n';}};
    ['focus','blur','pagehide','pageshow'].forEach(function(name){root.addEventListener(name,changed);});
    document.addEventListener('visibilitychange',changed);
    document.addEventListener('scroll',function(){sample();paint();},true);root.addEventListener('resize',function(){sample();paint();});
    new MutationObserver(changed).observe(document.body,{subtree:true,attributes:true,attributeFilter:['open','hidden']});
    document.addEventListener('brief:notes-changed',function(){enqueue();flush();paint();});
    // The exact-file server has no sibling-file read API. Keep local references
    // usable in the portable file and explain that boundary instead of navigating to a 404.
    if(cfg)document.addEventListener('click',function(event){var a=event.target.closest('a[href]');if(!a)return;var raw=a.getAttribute('href');if(raw.startsWith('#')||/^[a-z][a-z0-9+.-]*:/i.test(raw)&&!raw.startsWith('file:'))return;event.preventDefault();statusText='Local reference · open the original HTML in Terminal Delight to follow this link';paint();});
    sample();paint();
    if(enabled){setInterval(function(){sample();paint();},1000);setInterval(function(){enqueue();flush();},5000);flush();}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(globalThis);
