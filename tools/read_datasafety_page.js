// Read one Play Store Data safety page into a JSON record.
//
// PURPOSE: Run in the browser's console (or through a browser automation tool) on a page
// at https://play.google.com/store/apps/datasafety?id=<package>&hl=en_US. Returns the app
// name, developer, the data types under "Data shared" and "Data collected", whether the
// page says no data is shared, the four Security practices statements (encrypted in
// transit, deletion can be requested, Play Families Policy, independent security review),
// and the developer's privacy policy address. The result is
// pasted into sources/overrides.json. This is a person (or their agent) reading one page
// at a time in a browser; it is not a crawler and must not be run as one.
//
// Copyright (c) 2026 CYBERINE LLC. All rights reserved.
(() => {
  const types = ["Location","Personal info","Financial info","Health and fitness","Messages","Photos and videos","Audio","Files and docs","Calendar","Contacts","App activity","Web browsing","App info and performance","Device or other IDs"];
  const lines = document.body.innerText.split("\n").map(s => s.trim()).filter(Boolean);
  const tip = lines.indexOf("privacy_tip");
  const out = {pkg: new URL(location.href).searchParams.get("id"), name: document.title.replace(/ - Apps on Google Play$/, ""), developer: tip > 0 ? lines[tip-1] : null, shared: [], collected: [], noShared: false, noCollected: false, security: {encryptedInTransit: null, deletionRequest: null, familiesPolicy: false, independentReview: false}, policy: null, missing: /item not found|We're sorry/i.test(document.body.innerText)};
  let section = null;
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (l === "Data shared") section = "shared";
    else if (l === "Data collected") section = "collected";
    else if (l === "Security practices") section = "security";
    else if (l.startsWith("No data shared")) out.noShared = true;
    else if (l.startsWith("No data collected")) out.noCollected = true;
    else if (section === "security") {
      // The page states each practice as a sentence; the wording below is Google's own as of October 2026.
      if (/^Data is encrypted in transit/i.test(l)) out.security.encryptedInTransit = true;
      else if (/^Data isn.t encrypted/i.test(l)) out.security.encryptedInTransit = false;
      else if (/^You can request that data be deleted/i.test(l)) out.security.deletionRequest = true;
      else if (/^Data can.t be deleted/i.test(l)) out.security.deletionRequest = false;
      else if (/^Committed to follow the Play Families Policy/i.test(l)) out.security.familiesPolicy = true;
      else if (/^Independent security review/i.test(l)) out.security.independentReview = true;
    }
    else if (section && types.includes(l) && lines[i+2] === "expand_more") out[section].push(l);
  }
  const a = [...document.querySelectorAll("a")].find(x => /privacy policy/i.test(x.textContent) && !/policies\.google\.com/.test(x.href));
  out.policy = a ? a.href : null;
  return JSON.stringify(out);
})()
