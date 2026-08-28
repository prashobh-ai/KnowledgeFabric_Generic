/* Team-area gate. A convenience lock for presenter materials, not a vault:
 * the site is static, so this deters casual visitors and keeps the client
 * surface clean — it is not access control for anything sensitive. */
(function () {
  "use strict";
  var KEY = "aicoe_team";
  if (sessionStorage.getItem(KEY) === "1") return;
  document.documentElement.style.visibility = "hidden";
  function show() {
    document.documentElement.style.visibility = "";
    var o = document.createElement("div");
    o.id = "gate";
    o.innerHTML =
      '<style>#gate{position:fixed;inset:0;z-index:9999;background:#FBFCFD;display:grid;place-items:center;font-family:Inter,system-ui,sans-serif}' +
      '#gate .g{width:min(360px,88vw);background:#fff;border:1px solid #DFE7EE;border-radius:16px;padding:30px;box-shadow:0 30px 70px -40px rgba(10,22,38,.4);text-align:center}' +
      '#gate img{height:34px;margin-bottom:14px}' +
      '#gate h1{font-size:18px;font-weight:600;color:#0A1626;margin:0 0 4px}' +
      '#gate p{font-size:12.5px;color:#6A7F94;margin:0 0 18px}' +
      '#gate input{width:100%;box-sizing:border-box;border:1px solid #DFE7EE;border-radius:9px;padding:11px 13px;font-size:15px;text-align:center;letter-spacing:.12em}' +
      '#gate input:focus{outline:2px solid #0086E6;border-color:#0086E6}' +
      '#gate button{margin-top:12px;width:100%;border:0;border-radius:9px;background:#0086E6;color:#fff;font-weight:600;font-size:14px;padding:11px;cursor:pointer}' +
      '#gate .err{color:#D92D20;font-size:12px;height:16px;margin-top:8px}' +
      '#gate a{display:inline-block;margin-top:14px;font-size:12px;color:#6A7F94}</style>' +
      '<div class="g"><img src="' + (window.GATE_BASE || "../") + 'assets/brand/qualizeal-icon.png" alt="">' +
      '<h1>Team area</h1><p>QualiZeal AI-CoE presenter materials</p>' +
      '<form><input type="password" autocomplete="off" placeholder="Access code" autofocus>' +
      '<button type="submit">Enter</button><div class="err"></div></form>' +
      '<a href="' + (window.GATE_BASE || "../") + '">Back to Knowledge Fabric</a></div>';
    document.body.appendChild(o);
    var f = o.querySelector("form"), inp = o.querySelector("input"), err = o.querySelector(".err");
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (inp.value === "aicoe4u") {
        sessionStorage.setItem(KEY, "1");
        o.remove();
      } else {
        err.textContent = "Not quite — ask the AI-CoE team.";
        inp.select();
      }
    });
  }
  if (document.body) show();
  else document.addEventListener("DOMContentLoaded", show);
})();
