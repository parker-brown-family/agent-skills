import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const context={};
vm.runInNewContext(readFileSync(fileURLToPath(new URL('../assets/reading.js',import.meta.url)),'utf8'),context);
const Clock=context.BriefReadingClock;
const portable=JSON.parse(readFileSync(fileURLToPath(new URL('fixtures/reading/record.json',import.meta.url)),'utf8'));
assert.deepEqual(portable.sessions.map(s=>s.host),['browser','terminal-delight']);
const {targets:fixtureTargets,gaps:fixtureGaps,...fixtureIdentity}=portable.sessions[0];
const fixtureClock=new Clock(fixtureIdentity,fixtureTargets);
fixtureClock.sample(0,'active',['section-one'],['section-one','entry-one']);
fixtureClock.sample(1250,'inactive',[],['section-one','entry-one']);
assert.deepEqual(JSON.parse(JSON.stringify(fixtureClock.checkpoint().targets)),fixtureTargets,'one portable fixture describes JS, Python and Rust records');
function clock(){return new Clock({session:'test',document:'test-doc',revision:'sha256:'+'1'.repeat(64),host:'browser',method:1},[
  {anchor:'one',title:'One',kind:'section',parent:null},
  {anchor:'two',title:'Two',kind:'section',parent:null},
  {anchor:'unknown',title:'Unavailable',kind:'figure',parent:'two'}]);}
function value(c,key){return c.checkpoint().targets.find(t=>t.anchor===key).visible_ms;}

const still=clock();
still.sample(0,'active',['one'],['one','two']);
for(let second=1;second<=3600;second++)still.sample(second*1000,'active',['one'],['one','two']);
assert.equal(value(still,'one'),3600000,'still-active hour counts with no input');
assert.equal(value(still,'two'),0,'known but unseen stays zero');
assert.equal(value(still,'unknown'),null,'unavailable geometry remains unknown');
still.sample(3600000,'inactive',[],['one','two']);
for(let second=1;second<=86400;second++)still.sample(3600000+second*1000,'inactive',[],['one','two']);
assert.equal(value(still,'one'),3600000,'inactive day adds nothing');

const hidden=clock();hidden.sample(0,'inactive',[],['one']);hidden.sample(1000,'inactive',[],['one']);
assert.equal(hidden.checkpoint(),null,'no record is invented for a never-active renderer');

const scroll=clock();scroll.sample(0,'active',['one'],['one','two']);scroll.sample(1000,'active',['two'],['one','two']);scroll.sample(2000,'inactive',[],['one','two']);
assert.equal(value(scroll,'one'),1000,'transition settles previous viewport');
assert.equal(value(scroll,'two'),1000,'new viewport starts at transition');
scroll.sample(3000,'inactive',[],['one','two']);assert.equal(value(scroll,'two'),1000,'covered/inactive document pauses');

const sleep=clock();sleep.sample(0,'active',['one'],['one']);sleep.sample(60000,'active',['one'],['one']);
assert.equal(value(sleep,'one'),0,'sleep is not sixty seconds of invented reading');
assert.equal(sleep.checkpoint().gaps[0].elapsed_ms,60000);
sleep.sample(61000,'active',['one'],['one']);assert.equal(value(sleep,'one'),1000,'observation resumes after gap');

const unknown=clock();unknown.sample(0,'active',['one'],['one']);unknown.sample(1000,'unknown',[],['one']);unknown.sample(2000,'unknown',[],['one']);unknown.sample(3000,'active',['one'],['one']);
assert.equal(value(unknown,'one'),1000);assert.equal(unknown.checkpoint().gaps[0].elapsed_ms,2000);
const fractional=clock();fractional.sample(0,'active',['one'],['one']);fractional.sample(0.6,'active',['one'],['one']);fractional.sample(1.2,'active',['one'],['one']);
assert.equal(value(fractional,'one'),1,'fractional samples retain elapsed time');
assert.throws(()=>fractional.sample(0,'active',[],[]),/backwards/);
console.log(JSON.stringify({passed:true,stillActiveHourMs:value(still,'one'),inactiveDayAddedMs:0,unknownIsNull:true,previousViewport:true,suspendGap:true,neverActiveHasNoRecord:true}));
