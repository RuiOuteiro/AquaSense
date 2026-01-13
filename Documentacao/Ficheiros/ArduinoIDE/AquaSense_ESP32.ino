#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPAsyncWebServer.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// =====================
// CONFIGURAÇÃO WIFI
// =====================
const char* ssid = "Vodafone-93D0B8_EXT";
const char* password = "<pw>";

// =====================
// CONFIG BASE DE DADOS
// ====================
// Substituir com IP do servidor
const char* urlServidor = "http://192.168.1.139/aquasense/api/registar_leitura.php";
const char* chaveApi = "aquasense_chave_secreta_2024";
const unsigned long INTERVALO_REGISTO_BD_MS = 30000;


// =====================
// HARDWARE
// =====================
const int pinmosfet = 18;
const int freq = 5000;
const int resolution = 8;

// GPIO where the DS18B20 is connected to
const int oneWireBus = 2;

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

// =====================
// DHT
// =====================
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// =====================
// SERVER
// =====================
AsyncWebServer server(80);

// =====================
// ESTADO / CONFIG
// =====================
volatile bool modeAuto = true;

float tempC = NAN;
float humP  = NAN;
float tempWaterC = NAN;

unsigned long lastSensorRead = 0;
const unsigned long SENSOR_INTERVAL_MS = 2000;

unsigned long ultimoRegistoBD = 0;

// Limiares de temperatura e histerese
float T_LOW  = 24.0;
float T_HIGH = 28.0;
float HYST   = 0.3;

uint8_t manualPWM = 120;
uint8_t currentPWM = 0;
bool forcedOn = false;

// =====================
// HELPERS
// =====================
static String fmtFloat(float v, int decimals = 1) {
  if (isnan(v)) return "--";
  return String(v, decimals);
}
uint8_t clampU8(int v){ if(v<0) return 0; if(v>255) return 255; return (uint8_t)v; }

void applyPWM(uint8_t pwm) {
  currentPWM = pwm;
  // ESP32 core 3.x: escreve pelo PIN
  ledcWrite(pinmosfet, currentPWM);
}

void updateSensorIfNeeded() {
  unsigned long now = millis();
  if (now - lastSensorRead < SENSOR_INTERVAL_MS) return;
  lastSensorRead = now;

  float t = dht.readTemperature();
  float h = dht.readHumidity();
  //Temperatura da agua
  sensors.requestTemperatures(); 
  float tw = sensors.getTempCByIndex(0);

  if (!isnan(t)) tempC = t;
  if (!isnan(h)) humP  = h;
  if (!isnan(tw)) tempWaterC = tw;

}

// AUTO control (histerese + proporcional)
void controlLogic() {
  updateSensorIfNeeded();

  if (!modeAuto) {
    applyPWM(manualPWM);
    return;
  }

  if (isnan(tempC)) {
    applyPWM(0);
    forcedOn = false;
    return;
  }

  // Histerese: evita “piscar”
  if (forcedOn) {
    if (tempC <= (T_LOW - HYST)) {
      forcedOn = false;
      applyPWM(0);
      return;
    }
  } else {
    if (tempC >= (T_HIGH + HYST)) {
      forcedOn = true;
      applyPWM(255);
      return;
    }
  }

  // Zona proporcional
  if (tempC <= T_LOW) {
    applyPWM(0);
  } else if (tempC >= T_HIGH) {
    applyPWM(255);
    forcedOn = true;
  } else {
    float ratio = (tempC - T_LOW) / (T_HIGH - T_LOW); // 0..1
    applyPWM(clampU8((int)(ratio * 255.0f)));
  }
}

String tempZone() {
  if (isnan(tempC)) return "sem leitura";
  if (tempC < T_LOW) return "frio (OFF)";
  if (tempC > T_HIGH) return "quente (MAX)";
  return "intermédio (AUTO)";
}
String humZone() {
  if (isnan(humP)) return "sem leitura";
  if (humP < 35) return "seco";
  if (humP > 70) return "muito húmido";
  return "normal";
}
String globalState(String &msg){
  if (isnan(tempC) || isnan(humP)) { msg="Sensor a estabilizar / leitura falhou (DHT11 é lento)."; return "AVISO"; }
  if (tempC >= (T_HIGH + 1.5))     { msg="Temperatura elevada. Sistema a compensar com brilho alto."; return "ALERTA"; }
  msg="Tudo está estável. Controlo ativo e atualização em tempo real.";
  return "OK";
}

String buildStatusJson(){
  String msg; String state = globalState(msg);
  String json = "{";
  json += "\"temp\":\"" + fmtFloat(tempC,1) + "\",";
  json += "\"hum\":\""  + fmtFloat(humP,0) + "\",";
  json += "\"temp_num\":" + String(isnan(tempC) ? "null" : String(tempC,2)) + ",";
  json += "\"hum_num\":"  + String(isnan(humP)  ? "null" : String(humP,2)) + ",";
  json += "\"pwm\":" + String((int)currentPWM) + ",";
  json += "\"mode\":\"" + String(modeAuto ? "AUTO" : "MANUAL") + "\",";
  json += "\"t_low\":\"" + String(T_LOW,1) + "\",";
  json += "\"t_high\":\"" + String(T_HIGH,1) + "\",";
  json += "\"temp_zone\":\"" + tempZone() + "\",";
  json += "\"hum_zone\":\"" + humZone() + "\",";
  json += "\"state\":\"" + state + "\",";
  json += "\"message\":\"" + msg + "\"";
  json += "}";
  return json;
}

// =====================
// HTML (PROGMEM)
// =====================
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AquaSense • ESP32</title>
  <style>
    :root{
      --bg:#0b1220; --card:#101a2f; --txt:#e8eefc; --muted:#9fb0d0; --line:rgba(255,255,255,.08);
      --ok:#32d583; --warn:#fdb022; --bad:#f04438; --accent:#5b8cff;
      --shadow: 0 18px 40px rgba(0,0,0,.35); --r:18px;
    }
    *{box-sizing:border-box}
    body{
      margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;
      background: radial-gradient(1200px 700px at 20% 10%, rgba(91,140,255,.25), transparent 50%),
                  radial-gradient(900px 600px at 80% 0%, rgba(50,213,131,.18), transparent 55%),
                  var(--bg);
      color:var(--txt);
    }
    .wrap{max-width:980px;margin:0 auto;padding:28px 16px 36px}
    header{
      display:flex;gap:14px;align-items:center;justify-content:space-between;
      padding:14px 16px;border:1px solid var(--line);background:rgba(16,26,47,.65);
      border-radius:var(--r);box-shadow:var(--shadow);backdrop-filter: blur(10px);
    }
    .brand h1{margin:0;font-size:18px}
    .brand p{margin:0;color:var(--muted);font-size:12px}
    .pill{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);
      padding:8px 10px;border-radius:999px;background:rgba(15,25,48,.8);font-size:12px}
    .dot{width:9px;height:9px;border-radius:50%}
    .grid{display:grid;grid-template-columns:1.2fr .8fr;gap:14px;margin-top:14px}
    @media (max-width:820px){.grid{grid-template-columns:1fr}}
    .card{border:1px solid var(--line);background:rgba(16,26,47,.7);border-radius:var(--r);box-shadow:var(--shadow);overflow:hidden}
    .hd{padding:14px 16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;
      background:linear-gradient(180deg, rgba(15,25,48,.95), rgba(16,26,47,.65));}
    .hd strong{font-size:13px;color:var(--muted);font-weight:650}
    .bd{padding:16px}
    .kpis{display:grid;grid-template-columns:1fr 1fr;gap:12px}
    .kpi{border:1px solid var(--line);background:rgba(15,25,48,.7);border-radius:16px;padding:14px}
    .kpi .label{color:var(--muted);font-size:12px}
    .kpi .value{font-size:32px;font-weight:800;margin-top:8px}
    .kpi .sub{color:var(--muted);font-size:12px;margin-top:4px}
    .bar{height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;margin-top:10px}
    .bar > div{height:100%;width:0%;background:linear-gradient(90deg, rgba(91,140,255,.95), rgba(50,213,131,.9))}
    .row{display:flex;gap:10px;align-items:center;justify-content:space-between;margin-top:14px}
    .muted{color:var(--muted);font-size:12px}
    .alert{margin-top:12px;padding:12px;border-radius:14px;border:1px solid var(--line);background:rgba(15,25,48,.6);
      display:flex;gap:10px;align-items:flex-start}
    .alert b{font-size:13px}
    .box{border:1px solid var(--line);background:rgba(15,25,48,.7);border-radius:16px;padding:14px}
    .box h3{margin:0 0 6px 0;font-size:13px;color:var(--muted);font-weight:700}
    .toggle{display:flex;gap:10px;align-items:center;justify-content:space-between;margin-top:10px}
    .switch{width:54px;height:30px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid var(--line);position:relative;cursor:pointer}
    .switch::after{content:"";position:absolute;top:3px;left:3px;width:24px;height:24px;border-radius:50%;background:#fff;transition:.2s}
    .switch.on{background:rgba(50,213,131,.25)}
    .switch.on::after{left:27px}
    input[type="range"]{width:100%}
    .small{display:flex;justify-content:space-between;gap:10px;margin-top:8px;font-size:12px;color:var(--muted)}
    footer{margin-top:14px;color:var(--muted);font-size:12px;text-align:center}
    code{color:var(--accent)}
  </style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">
      <h1>AquaSense • ESP32 Climate</h1>
      <p>DHT11 + PWM (12V via MOSFET) • Auto/Manual</p>
    </div>
    <div class="pill">
      <span class="dot" id="dot" style="background:var(--warn)"></span>
      <span id="modePill">A iniciar...</span>
    </div>
  </header>

  <div class="grid">
    <section class="card">
      <div class="hd">
        <strong>Dashboard</strong>
        <span class="muted">Atualiza a cada 2s</span>
      </div>
      <div class="bd">
        <div class="kpis">
          <div class="kpi">
            <div class="label">Temperatura</div>
            <div class="value"><span id="t">--</span><span style="font-size:16px;color:var(--muted)"> °C</span></div>
            <div class="sub">Zona: <span id="zoneT">--</span></div>
            <div class="bar"><div id="barT"></div></div>
          </div>
          <div class="kpi">
            <div class="label">Humidade</div>
            <div class="value"><span id="h">--</span><span style="font-size:16px;color:var(--muted)"> %</span></div>
            <div class="sub">Conforto: <span id="zoneH">--</span></div>
            <div class="bar"><div id="barH"></div></div>
          </div>
        </div>

        <div class="alert">
          <div class="dot" id="alertDot" style="background:var(--warn); margin-top:3px"></div>
          <div>
            <b id="alertTitle">Estado</b>
            <div class="muted" id="alertText">A carregar dados...</div>
          </div>
        </div>

        <div class="row">
          <div class="muted">Brilho atual (PWM)</div>
          <div style="font-weight:800"><span id="pwm">0</span>/255</div>
        </div>
        <div class="bar"><div id="barPWM"></div></div>
      </div>
    </section>

    <aside class="card">
      <div class="hd"><strong>Controlo</strong><span class="muted">Auto / Manual</span></div>
      <div class="bd">
        <div class="box">
          <h3>Modo</h3>
          <div class="toggle">
            <div>
              <div style="font-weight:850" id="modeLabel">AUTO</div>
              <div class="muted">AUTO ajusta brilho pela temperatura</div>
            </div>
            <div class="switch on" id="sw"></div>
          </div>
        </div>

        <div class="box" style="margin-top:12px">
          <h3>Temperatura (AUTO)</h3>
          <div class="muted">Abaixo de <b id="tLowLbl">--</b>°C OFF • Acima de <b id="tHighLbl">--</b>°C MAX</div>

          <div style="margin-top:10px">
            <label class="muted">T_LOW</label>
            <input id="tLow" type="range" min="10" max="35" step="0.5" value="24">
            <div class="small"><span>10°C</span><span id="tLowVal">24.0°C</span><span>35°C</span></div>
          </div>

          <div style="margin-top:10px">
            <label class="muted">T_HIGH</label>
            <input id="tHigh" type="range" min="12" max="40" step="0.5" value="28">
            <div class="small"><span>12°C</span><span id="tHighVal">28.0°C</span><span>40°C</span></div>
          </div>
        </div>

        <div class="box" style="margin-top:12px">
          <h3>Brilho (MANUAL)</h3>
          <input id="manual" type="range" min="0" max="255" step="1" value="120">
          <div class="small"><span>0</span><span id="manualVal">120</span><span>255</span></div>
        </div>

      </div>
    </aside>
  </div>

  <footer>API: <code>/api/status</code> • Config: <code>/api/config?mode=auto</code></footer>
</div>

<script>
const el = (id)=>document.getElementById(id);
function setBar(barEl, percent){
  const p = Math.max(0, Math.min(100, percent));
  barEl.style.width = p + "%";
}
async function fetchStatus(){
  const r = await fetch("/api/status", {cache:"no-store"});
  const j = await r.json();

  el("t").textContent = j.temp;
  el("h").textContent = j.hum;
  el("pwm").textContent = j.pwm;

  el("modeLabel").textContent = j.mode;
  el("modePill").textContent = j.mode + " • " + j.state;

  el("tLowLbl").textContent = j.t_low;
  el("tHighLbl").textContent = j.t_high;

  el("zoneT").textContent = j.temp_zone;
  el("zoneH").textContent = j.hum_zone;

  // switch + dots
  el("sw").classList.toggle("on", j.mode === "AUTO");
  el("dot").style.background = (j.state === "OK") ? "var(--ok)" : (j.state==="ALERTA" ? "var(--bad)" : "var(--warn)");
  el("alertDot").style.background = el("dot").style.background;

  el("alertTitle").textContent = j.state;
  el("alertText").textContent = j.message;

  // bars
  setBar(el("barPWM"), (j.pwm/255)*100);

  const tVal = (j.temp_num === null) ? 0 : j.temp_num;
  setBar(el("barT"), (tVal/45)*100);

  const hVal = (j.hum_num === null) ? 0 : j.hum_num;
  setBar(el("barH"), hVal);
}

async function sendConfig(params){
  const qs = new URLSearchParams(params).toString();
  await fetch("/api/config?" + qs, {cache:"no-store"});
  await fetchStatus();
}

const tLow = el("tLow");
const tHigh = el("tHigh");
const manual = el("manual");

function updateLabels(){
  el("tLowVal").textContent = parseFloat(tLow.value).toFixed(1) + "°C";
  el("tHighVal").textContent = parseFloat(tHigh.value).toFixed(1) + "°C";
  el("manualVal").textContent = manual.value;
}
updateLabels();

el("sw").addEventListener("click", async ()=>{
  const wantAuto = !el("sw").classList.contains("on");
  await sendConfig({mode: wantAuto ? "auto" : "manual"});
});

tLow.addEventListener("input", updateLabels);
tHigh.addEventListener("input", updateLabels);
manual.addEventListener("input", updateLabels);

tLow.addEventListener("change", async ()=>{ await sendConfig({t_low:tLow.value, t_high:tHigh.value}); });
tHigh.addEventListener("change", async ()=>{ await sendConfig({t_low:tLow.value, t_high:tHigh.value}); });
manual.addEventListener("change", async ()=>{ await sendConfig({manual:manual.value}); });

fetchStatus();
setInterval(fetchStatus, 2000);
</script>
</body>
</html>
)rawliteral";

// =====================
// SETUP / LOOP
// =====================
void setup() {
  Serial.begin(115200);

  // PWM init (ESP32 core 3.x)
  ledcAttach(pinmosfet, freq, resolution);

  // Start the DS18B20 sensor
  sensors.begin();

  applyPWM(0);

  dht.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(600);
    Serial.println("Connecting to WiFi..");
  }
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Página
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html);
  });

  // Status JSON
  server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "application/json", buildStatusJson());
  });

  // Config:
  // /api/config?mode=auto|manual&t_low=24&t_high=28&manual=120
  server.on("/api/config", HTTP_GET, [](AsyncWebServerRequest *request){
    if (request->hasParam("mode")) {
      String m = request->getParam("mode")->value();
      m.toLowerCase();
      modeAuto = (m == "auto");
    }
    if (request->hasParam("t_low"))  T_LOW  = request->getParam("t_low")->value().toFloat();
    if (request->hasParam("t_high")) T_HIGH = request->getParam("t_high")->value().toFloat();
    if (request->hasParam("manual")) manualPWM = (uint8_t)request->getParam("manual")->value().toInt();

    // safety: garante T_HIGH > T_LOW
    if (T_HIGH <= T_LOW + 0.5f) T_HIGH = T_LOW + 0.5f;

    request->send(200, "text/plain", "OK");
  });

  server.begin();
}

// =====================
// REGISTO NA BASE DE DADOS
// =====================
void registarNaBaseDados() {
  unsigned long agora = millis();
  if (agora - ultimoRegistoBD < INTERVALO_REGISTO_BD_MS) 
    return;
  ultimoRegistoBD = agora;

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[BD] WiFi desligado, a saltar registo");
    return;
  }

  if (isnan(tempC) || isnan(humP)) {
    Serial.println("[BD] Sem dados válidos do sensor, a saltar registo");
    return;
  }

  Serial.print("[SENSOR] T=");
  Serial.print(fmtFloat(tempC, 1));
  Serial.print("C  H=");
  Serial.print(fmtFloat(humP, 0));
  Serial.println("%");

  Serial.print("[SENSORWATER] T=");
  Serial.print(fmtFloat(tempWaterC, 1));
  Serial.println("C");
  
  HTTPClient http;
  http.begin(urlServidor);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", chaveApi);

  String jsonDados = "{";
  jsonDados += "\"temperatura\":" + String(tempC, 2) + ",";
  jsonDados += "\"humidade\":" + String(humP, 2) + ",";
  jsonDados += "\"pwm\":" + String((int)currentPWM) + ",";
  jsonDados += "\"modo\":\"" + String(modeAuto ? "AUTO" : "MANUAL") + "\",";
  jsonDados += "\"t_minima\":" + String(T_LOW, 1) + ",";
  jsonDados += "\"t_maxima\":" + String(T_HIGH, 1) + ",";
  jsonDados += "\"t_agua\":" + String(tempWaterC, 2);
  jsonDados += "}";

  int codigoHttp = http.POST(jsonDados);

  if (codigoHttp > 0) {
    String resposta = http.getString();
    Serial.print("[BD] HTTP ");
    Serial.print(codigoHttp);
    Serial.print(" - ");
    Serial.println(resposta);
  } else {
    Serial.print("[BD] Erro: ");
    Serial.println(http.errorToString(codigoHttp));
  }

  http.end();
}

void loop() {
  controlLogic();
  registarNaBaseDados();
  delay(5);
}