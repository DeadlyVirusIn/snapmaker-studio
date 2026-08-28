// Two throwaway HTTP servers the acceptance run owns, for the two provider
// questions that cannot be answered by pointing Studio at a real provider.
//
//  * The **counting probe** answers both providers' list routes with an empty
//    inventory and counts every request it receives. That turns "no provider is
//    configured" from an assertion into a measurement: configure it, see the
//    count rise; select None, see it not move.
//
//  * The **redirect probe** answers every request with `302` to a public host.
//    A local address is not a promise about where the *second* request goes, and
//    this is the only way to prove the installed build refuses to follow one —
//    the defect it is checking for was real, and it was in the shared transport
//    rather than in any one provider.
//
// Both listen on the loopback only, are started by the acceptance driver, and
// die with it. Usage:  node probes.mjs <countPort> <redirectPort>

import { createServer } from "node:http";

const [, , countPort, redirectPort] = process.argv;

let hits = 0;
const seen = [];

createServer((req, res) => {
  if (req.url === "/__hits") {
    // Read by the driver directly, never through Studio, so it cannot itself be
    // mistaken for provider traffic.
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ hits, seen }));
    return;
  }
  hits += 1;
  seen.push(req.url);
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end("[]");
}).listen(Number(countPort), "127.0.0.1", () => {
  console.log(`counting probe on ${countPort}`);
});

createServer((req, res) => {
  res.writeHead(302, { Location: "http://example.com/api/v1/spool" });
  res.end();
}).listen(Number(redirectPort), "127.0.0.1", () => {
  console.log(`redirect probe on ${redirectPort}`);
});
