// Quick test of Jewelry XRF analysis logic
const MD={Au:19.30,Pt:21.45,Pd:12.02,Ag:10.49,Cu:8.96,Ni:8.91,Zn:7.13,Fe:7.87,Sn:7.31,Pb:11.34,W:19.25,Rh:12.41,Ir:22.56,Os:22.59,Ru:12.37,Cd:8.65,Brass:8.55,Bronze:8.80,Steel:7.85};
const STONE_DEN={diamond:3.52,ruby:4.00,emerald:2.72,garnet:3.80,zircon:5.80,pearl:2.71,topaz:3.53,quartz:2.65,glass:2.50,unknown:3.00};
const SOLDER_EST={ring:[2,3,14],chain:[5,8,12],bangle:[3,5,14],necklace:[4,6,12],earring:[3,5,12],pendant:[2,3,14],set:[4,6,12],coin:[0,1,22],bar:[0,0,24],plain:[1,2,14]};

function ternaryModel(density){
    const dAu=MD.Au,dAg=MD.Ag,dCu=MD.Cu;const invD=1/density,invAu=1/dAu,invAg=1/dAg,invCu=1/dCu;
    const goldFracCu=Math.max(0,Math.min(1,(invCu-invD)/(invCu-invAu)));
    let agRatio;if(goldFracCu>.95)agRatio=.5;else if(goldFracCu>.85)agRatio=.55;else if(goldFracCu>.70)agRatio=.40;else if(goldFracCu>.55)agRatio=.30;else agRatio=.25;
    const alloyPart=1-goldFracCu;let xAu=goldFracCu,xAg=alloyPart*agRatio,xCu=alloyPart*(1-agRatio);
    for(let i=0;i<5;i++){const calcInvD=xAu*invAu+xAg*invAg+xCu*invCu;const error=invD-calcInvD;const adj=error/(invAu-(agRatio*invAg+(1-agRatio)*invCu));xAu=Math.max(0,Math.min(1,xAu+adj));xAg=(1-xAu)*agRatio;xCu=(1-xAu)*(1-agRatio);}
    return {Au:Math.max(0,xAu)*100,Ag:Math.max(0,xAg)*100,Cu:Math.max(0,xCu)*100};
}

function analyzeJewelry(wA, wW, hasStones, stoneType, stoneWt, jType, claimedK){
    const wd=0.99705;// 25°C
    const diff=wA-wW;
    const vol=diff/wd;
    const overallDensity=wA/vol;
    
    let metalDensity=overallDensity;
    let metalWt=wA;
    const stoneDen=STONE_DEN[stoneType]||3.00;
    let stoneVolume=0;

    if(hasStones){
        if(stoneWt>0 && stoneWt<wA){
            stoneVolume=stoneWt/stoneDen;
            metalWt=wA-stoneWt;
            const metalVol=vol-stoneVolume;
            if(metalVol>0) metalDensity=metalWt/metalVol;
        }
    }

    // Material detection
    let tern, karat, materialType='gold';
    if(metalDensity>=10.20 && metalDensity<=10.60){
        materialType='silver';
        const agPct=Math.min(99.9,80+(metalDensity-10.20)/(10.49-10.20)*19.9);
        tern={Au:0,Ag:agPct,Cu:100-agPct};
        karat=0;
    } else if(metalDensity>=21.0 && metalDensity<=21.9){
        materialType='platinum';
        tern={Au:0,Ag:0,Cu:5};
        karat=0;
    } else if(metalDensity<10.20){
        materialType='base';
        tern={Au:0,Ag:0,Cu:100};
        karat=0;
    } else {
        tern=ternaryModel(metalDensity);
        karat=tern.Au/100*24;
    }
    
    let elements={Au:tern.Au, Ag:tern.Ag, Cu:tern.Cu};
    
    if(materialType==='platinum') elements={Pt:95,Ir:3,Rh:2};
    else if(materialType==='base'){
        if(metalDensity>=8.3&&metalDensity<=9.1) elements={Cu:65,Zn:35};
        else if(metalDensity>=7.5&&metalDensity<=8.1) elements={Fe:70,Cr:18,Ni:12};
        else elements={Cu:50,Zn:25,Ni:15,Fe:10};
    }
    
    // Trace elements (gold only)
    let cdPct=0;
    if(materialType==='gold'){
        if(karat<22 && karat>0) elements.Zn=Math.min(3,(24-karat)/24*4*0.3);
        if(karat<21 && karat>0) elements.Ni=Math.min(2,(24-karat)/24*3*0.15);
        
        const expectedDen=1/(tern.Au/100/MD.Au + tern.Ag/100/MD.Ag + tern.Cu/100/MD.Cu);
        if(metalDensity < expectedDen-0.05 && metalDensity > 8 && karat>0){
            const denDrop=expectedDen-metalDensity;
            cdPct=Math.min(5, denDrop/(MD.Cu-MD.Cd)*elements.Cu*0.5);
            if(cdPct>0.01){ elements.Cd=cdPct; elements.Cu=Math.max(0,elements.Cu-cdPct); }
        }
    }
    
    // Rebalance
    const tot=Object.values(elements).reduce((s,v)=>s+v,0);
    if(tot>0) Object.keys(elements).forEach(k=>elements[k]*=100/tot);
    
    // Solder
    const solderData=SOLDER_EST[jType]||[1,2,14];
    let solderPct=0, solderKarat=solderData[2];
    if(claimedK>0 && karat>0 && claimedK>karat && claimedK>solderKarat){
        solderPct=Math.min(15, Math.max(0,(claimedK-karat)/(claimedK-solderKarat)*100));
    } else {
        solderPct=(solderData[0]+solderData[1])/2;
    }

    return {overallDensity, metalDensity, karat, elements, cdPct, solderPct, solderKarat, metalWt, stoneVolume, materialType};
}

console.log('═══════════════════════════════════════════');
console.log('    JEWELRY XRF ENGINE — VERIFICATION');
console.log('═══════════════════════════════════════════\n');

// Test 1: 22K Gold Ring, no stones, 10g 
console.log('--- Test 1: 22K Gold Ring (no stones) ---');
// 22K ternary density ≈ 17.841
// wA=10g, wW = wA - wA/d * wd = 10 - 10/17.841*0.99705 ≈ 10-0.559 = 9.441
let r1=analyzeJewelry(10, 9.441, false, 'unknown', 0, 'ring', 22);
console.log(`  Overall Density: ${r1.overallDensity.toFixed(3)} (expected ~17.8)`);
console.log(`  Karat: ${r1.karat.toFixed(2)}K (expected ~22K)`);
console.log(`  Elements: Au=${r1.elements.Au?.toFixed(2)}% Ag=${r1.elements.Ag?.toFixed(2)}% Cu=${r1.elements.Cu?.toFixed(2)}% Zn=${r1.elements.Zn?.toFixed(2)||'0'}% Ni=${r1.elements.Ni?.toFixed(2)||'0'}%`);
console.log(`  Cadmium: ${r1.cdPct.toFixed(3)}%`);
console.log(`  Solder: ${r1.solderPct.toFixed(1)}% (${r1.solderKarat}K)`);
console.log(`  ✅ ${r1.karat>21.5 && r1.karat<22.5 ? 'PASS' : 'FAIL'}`);

// Test 2: 18K Gold Chain, no stones, claimed 18K
console.log('\n--- Test 2: 18K Gold Chain ---');
// 18K density ≈ 15.353
// wW = 10 - 10/15.353*0.99705 ≈ 10 - 0.649 = 9.351
let r2=analyzeJewelry(10, 9.351, false, 'unknown', 0, 'chain', 18);
console.log(`  Karat: ${r2.karat.toFixed(2)}K (expected ~18K)`);
console.log(`  Elements: Au=${r2.elements.Au?.toFixed(2)}% Ag=${r2.elements.Ag?.toFixed(2)}% Cu=${r2.elements.Cu?.toFixed(2)}%`);
console.log(`  Cd=${r2.elements.Cd?.toFixed(3)||'0'}% Zn=${r2.elements.Zn?.toFixed(2)||'0'}% Ni=${r2.elements.Ni?.toFixed(2)||'0'}%`);
console.log(`  Solder: ${r2.solderPct.toFixed(1)}% (chain: 5-8%)`);
console.log(`  ✅ ${r2.karat>17.5 && r2.karat<18.5 ? 'PASS' : 'FAIL'}`);

// Test 3: Jewelry WITH STONES — same 22K but lower overall density due to ruby
console.log('\n--- Test 3: 22K with Ruby stones (1g stone in 10g total) ---');
// Metal= 9g at d=17.841, Stone= 1g ruby at d=4.00
// Total vol = 9/17.841 + 1/4.00 = 0.5045 + 0.25 = 0.7545 cm³
// Overall density = 10/0.7545 = 13.254
// wW = wA - vol*wd = 10 - 0.7545*0.99705 = 10 - 0.7523 = 9.248
let r3=analyzeJewelry(10, 9.248, true, 'ruby', 1, 'ring', 22);
console.log(`  Overall Density: ${r3.overallDensity.toFixed(3)} (with stones, should be ~13.2)`);
console.log(`  Metal Density: ${r3.metalDensity.toFixed(3)} (should be ~17.8)`);
console.log(`  Karat: ${r3.karat.toFixed(2)}K (should be ~22K after stone correction)`);
console.log(`  Stone Volume: ${r3.stoneVolume.toFixed(4)} cm³`);
console.log(`  ✅ ${r3.karat>21 && r3.karat<23 ? 'PASS — Stone correction works!' : 'FAIL'}`);

// Test 4: Claimed 22K but actually 20K (solder detection)
console.log('\n--- Test 4: Claimed 22K but actual 20K (solder gap) ---');
// 20K density: calcD(20) 
let r4=analyzeJewelry(10, 9.365, false, 'unknown', 0, 'chain', 22);
console.log(`  Karat: ${r4.karat.toFixed(2)}K`);
console.log(`  Claimed: 22K, Measured: ${r4.karat.toFixed(1)}K`);
console.log(`  Solder estimate: ${r4.solderPct.toFixed(1)}% at ${r4.solderKarat}K`);
console.log(`  ✅ Solder gap ${r4.solderPct > 0 ? 'DETECTED' : 'NOT detected'}`);

// Test 5: Silver jewelry (not gold)
console.log('\n--- Test 5: Pure Silver Bangle ---');
// d=10.49, wW = 10 - 10/10.49*0.99705 = 10 - 0.9506 = 9.049
let r5=analyzeJewelry(10, 9.049, false, 'unknown', 0, 'bangle', 0);
console.log(`  Density: ${r5.overallDensity.toFixed(3)} (expected ~10.49)`);
console.log(`  Material: ${r5.materialType} (should be 'silver')`);
console.log(`  Karat: ${r5.karat} (should be 0 for silver)`);
console.log(`  Elements: Au=${r5.elements.Au?.toFixed(2)||'0'}% Ag=${r5.elements.Ag?.toFixed(2)}% Cu=${r5.elements.Cu?.toFixed(2)}%`);
console.log(`  ✅ ${r5.materialType==='silver' && r5.karat===0 && r5.elements.Ag>90 ? 'PASS — Silver correctly detected!' : 'FAIL'}`);

console.log('\n═══════════════════════════════════════════');
console.log('    ALL TESTS COMPLETE');
console.log('═══════════════════════════════════════════');
