const API_BASE_URL="";
const map=L.map("map",{center:[0.0236,37.9062],zoom:6,zoomControl:false});
const streetLayer=L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"&copy; OpenStreetMap contributors"});
const satelliteLayer=L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Tiles &copy; Esri"});
streetLayer.addTo(map);
L.control.zoom({position:"bottomright"}).addTo(map);
L.control.layers({"Street Map":streetLayer,"Satellite":satelliteLayer},null,{position:"topright",collapsed:true}).addTo(map);

const searchInput=document.getElementById("search-input");
const searchButton=document.getElementById("search-button");
const dashboardButton=document.getElementById("dashboard-button");
const dashboardPanel=document.getElementById("dashboard-panel");
const closeDashboardButton=document.getElementById("close-dashboard");
const aiQuestion=document.getElementById("ai-question");
const sendQuestionButton=document.getElementById("send-question");
const mobileAiToggle=document.getElementById("mobile-ai-toggle");
const mobileAiClose=document.getElementById("mobile-ai-close");
const aiPanel=document.getElementById("ai-panel");
const aiToggle =document.getElementById("ai-toggle");
const chatMessages=document.getElementById("chat-messages");
const suggestionButtons=document.querySelectorAll(".suggestion-button");
const mapStatus=document.getElementById("map-status");
const layersToggle=document.getElementById("layers-toggle");
const layerPanel=document.getElementById("layer-panel");

const spatialLayers={};
const enabledLayers=new Set();
const loadingControllers={};
let aiResultLayer=null;

const layerLimits={counties:100,constituencies:500,wards:1000,schools:5000,hospitals:5000,police:5000,roads:3000,fiber:2000,electricity:2000};

const layerButtons={
counties:document.getElementById("toggle-counties"),
constituencies:document.getElementById("toggle-constituencies"),
wards:document.getElementById("toggle-wards"),
schools:document.getElementById("toggle-schools"),
hospitals:document.getElementById("toggle-hospitals"),
police:document.getElementById("toggle-police"),
roads:document.getElementById("toggle-roads"),
fiber:document.getElementById("toggle-fiber"),
electricity:document.getElementById("toggle-electricity")
};

const layerStyles={
counties:{color:"#1f4e79",weight:2,fillOpacity:.05},
constituencies:{color:"#2e75b6",weight:1.5,fillOpacity:.08},
wards:{color:"#70ad47",weight:1,fillOpacity:.05},
schools:{radius:5,color:"#2e75b6",weight:1,fillOpacity:.8},
hospitals:{radius:6,color:"#c0392b",weight:1,fillOpacity:.8},
police:{radius:6,color:"#34495e",weight:1,fillOpacity:.8},
roads:{color:"#666666",weight:2,opacity:.8},
fiber:{color:"#8e44ad",weight:3,opacity:.8},
electricity:{color:"#f39c12",weight:3,opacity:.8},
analysis:{color:"#8e44ad",weight:3,fillOpacity:.25,opacity:.9}
};

function updateMapStatus(message){
if(mapStatus)mapStatus.textContent=`● ${message}`;
}

function formatLayerName(layerName){
return layerName.replace(/_/g," ").replace(/\b\w/g,letter=>letter.toUpperCase());
}

function getMapBoundingBox(){
const bounds=map.getBounds();
return{min_lon:bounds.getWest(),min_lat:bounds.getSouth(),max_lon:bounds.getEast(),max_lat:bounds.getNorth()};
}

async function loadLayer(layerName){
const bbox=getMapBoundingBox();
const params=new URLSearchParams({
min_lon:bbox.min_lon,
min_lat:bbox.min_lat,
max_lon:bbox.max_lon,
max_lat:bbox.max_lat,
limit:layerLimits[layerName]||2000
});
const url=`${API_BASE_URL}/api/layers/${layerName}?${params.toString()}`;
if(loadingControllers[layerName])loadingControllers[layerName].abort();
const controller=new AbortController();
loadingControllers[layerName]=controller;
try{
updateMapStatus(`Loading ${formatLayerName(layerName)}...`);
const response=await fetch(url,{signal:controller.signal});
if(!response.ok)throw new Error(`${layerName} request failed with status ${response.status}`);
const geojson=await response.json();
if(!geojson||geojson.type!=="FeatureCollection")throw new Error(`${layerName} returned invalid GeoJSON`);
if(spatialLayers[layerName])map.removeLayer(spatialLayers[layerName]);
spatialLayers[layerName]=createLeafletLayer(layerName,geojson);
spatialLayers[layerName].addTo(map);
updateMapStatus(`${formatLayerName(layerName)} loaded`);
console.log(`${layerName}: ${geojson.features.length} features loaded`);
}catch(error){
if(error.name==="AbortError")return;
console.error(`Failed to load ${layerName}:`,error);
updateMapStatus(`Failed to load ${formatLayerName(layerName)}`);
}
}

function createLeafletLayer(layerName,geojson){
const style=layerStyles[layerName]||{};
if(layerName==="schools"||layerName==="hospitals"||layerName==="police"){
return L.geoJSON(geojson,{
pointToLayer:function(feature,latlng){
return L.circleMarker(latlng,{radius:style.radius||5,color:style.color,weight:style.weight||1,fillOpacity:style.fillOpacity||.8});
},
onEachFeature:function(feature,layer){bindFeaturePopup(layerName,feature,layer);}
});
}
return L.geoJSON(geojson,{
style:style,
onEachFeature:function(feature,layer){
bindFeaturePopup(layerName,feature,layer);
layer.on({
mouseover:function(){
layer.setStyle({weight:(style.weight||1)+2,fillOpacity:.2});
},
mouseout:function(){
if(spatialLayers[layerName])spatialLayers[layerName].resetStyle(layer);
}
});
}
});
}

function bindFeaturePopup(layerName,feature,layer){
const properties=feature.properties||{};
let content=`<div class="map-popup"><strong>${formatLayerName(layerName)}</strong>`;
const fields=["county_name","constituency_name","ward_name","county_code","constituency_code","ward_code","school_name","hospital_name","police_name","name","facility_name","school_count","hospital_count","police_count","coverage_score"];
fields.forEach(field=>{
if(properties[field]!==null&&properties[field]!==undefined&&properties[field]!==""){
const label=field.replace(/_/g," ").replace(/\b\w/g,letter=>letter.toUpperCase());
content+=`<br>${label}: ${properties[field]}`;
}
});
content+=`</div>`;
layer.bindPopup(content);
}

async function enableLayer(layerName){
enabledLayers.add(layerName);
if(layerButtons[layerName])layerButtons[layerName].checked=true;
await loadLayer(layerName);
}

function disableLayer(layerName){
enabledLayers.delete(layerName);
if(layerButtons[layerName])layerButtons[layerName].checked=false;
if(loadingControllers[layerName]){
loadingControllers[layerName].abort();
delete loadingControllers[layerName];
}
if(spatialLayers[layerName]){
map.removeLayer(spatialLayers[layerName]);
delete spatialLayers[layerName];
}
}

async function toggleLayer(layerName){
if(enabledLayers.has(layerName)){
disableLayer(layerName);
updateMapStatus(`${formatLayerName(layerName)} hidden`);
return;
}
await enableLayer(layerName);
}

Object.entries(layerButtons).forEach(([layerName,checkbox])=>{
if(!checkbox)return;
checkbox.addEventListener("change",async function(){await toggleLayer(layerName);});
});

if(layersToggle&&layerPanel){
layersToggle.addEventListener("click",function(event){
event.stopPropagation();
const isOpen=layerPanel.classList.toggle("open");
layersToggle.setAttribute("aria-expanded",isOpen?"true":"false");
});
}

let moveTimer=null;
map.on("moveend",function(){
clearTimeout(moveTimer);
moveTimer=setTimeout(async function(){
if(enabledLayers.size===0)return;
updateMapStatus("Updating visible layers...");
const layersToUpdate=Array.from(enabledLayers);
for(const layerName of layersToUpdate)await loadLayer(layerName);
updateMapStatus("Map updated");
},700);
});

function openMobileAI(){
if(!aiPanel)return;
aiPanel.classList.add("mobile-open");
if(mobileAiToggle){
mobileAiToggle.setAttribute("aria-expanded","true");
mobileAiToggle.style.display="none";
}
setTimeout(function(){
map.invalidateSize();
if(aiQuestion)aiQuestion.focus();
},350);
}

function closeMobileAI(){
if(!aiPanel)return;
aiPanel.classList.remove("mobile-open");
if(mobileAiToggle){
mobileAiToggle.setAttribute("aria-expanded","false");
mobileAiToggle.style.display="";
}
setTimeout(function(){map.invalidateSize();},350);
}

mobileAiToggle?.addEventListener("click",openMobileAI);
mobileAiClose?.addEventListener("click",closeMobileAI);

window.addEventListener("resize",function(){
setTimeout(function(){map.invalidateSize();},150);
});

function openDashboard(){
if(dashboardPanel)dashboardPanel.classList.remove("hidden");
loadDashboard();
loadDashboardCounts();
}

function closeDashboard(){
if(dashboardPanel)dashboardPanel.classList.add("hidden");
}

async function loadDashboard(){
try{
const response=await fetch(`${API_BASE_URL}/api/dashboard/summary`);
if(!response.ok)throw new Error(`Dashboard request failed: ${response.status}`);
const data=await response.json();
const facilityCanvas=document.getElementById("facility-chart");
if(facilityCanvas){
if(window.facilityChart)window.facilityChart.destroy();
window.facilityChart=new Chart(facilityCanvas,{
type:"bar",
data:{
labels:["Health Facilities","Schools","Police Facilities"],
datasets:[{label:"National Total",data:[data.hospitals,data.schools,data.police]}]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}},
scales:{y:{beginAtZero:true,ticks:{callback:function(value){return Number(value).toLocaleString();}}}}
}
});
}
const coverageCanvas=document.getElementById("coverage-chart");
if(coverageCanvas){
if(window.coverageChart)window.coverageChart.destroy();
window.coverageChart=new Chart(coverageCanvas,{
type:"bar",
data:{
labels:["Roads","Electricity","Fiber"],
datasets:[{label:"Infrastructure Features",data:[data.roads,data.electricity,data.fiber]}]
},
options:{
indexAxis:"y",
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}},
scales:{x:{type:"logarithmic",min:1,ticks:{callback:function(value){return Number(value).toLocaleString();}}}}
}
});
}
}catch(error){
console.error("Dashboard loading error:",error);
}
}

dashboardButton?.addEventListener("click",openDashboard);
closeDashboardButton?.addEventListener("click",closeDashboard);

async function loadDashboardCounts(){
const datasets={health:"health-count",schools:"school-count",police:"police-count",counties:"county-count"};
for(const [dataset,elementId] of Object.entries(datasets)){
const element=document.getElementById(elementId);
if(!element)continue;
try{
const response=await fetch(`${API_BASE_URL}/api/analysis/count/${dataset}`);
if(!response.ok)throw new Error(`Count request failed: ${response.status}`);
const data=await response.json();
element.textContent=data.count;
}catch(error){
console.error(`Failed to load ${dataset} count:`,error);
element.textContent="N/A";
}
}
}

function addUserMessage(question){
if(!chatMessages)return;
const message=document.createElement("div");
message.className="message user-message";
const label=document.createElement("div");
label.className="message-label";
label.textContent="YOU";
const text=document.createElement("p");
text.textContent=question;
message.appendChild(label);
message.appendChild(text);
chatMessages.appendChild(message);
chatMessages.scrollTop=chatMessages.scrollHeight;
}

function addAssistantMessage(messageText){
if(!chatMessages)return;
const message=document.createElement("div");
message.className="message assistant-message";
const label=document.createElement("div");
label.className="message-label";
label.textContent="AI HELPER";
const text=document.createElement("p");
text.textContent=messageText;
message.appendChild(label);
message.appendChild(text);
chatMessages.appendChild(message);
chatMessages.scrollTop=chatMessages.scrollHeight;
}

async function askAIQuestion(question){
const cleanQuestion=question.trim();
if(!cleanQuestion)return;
addUserMessage(cleanQuestion);
if(aiQuestion)aiQuestion.value="";
updateMapStatus("Sending question...");
try{
const response=await fetch(`${API_BASE_URL}/api/analysis/ask`,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({question:cleanQuestion})
});
if(!response.ok)throw new Error(`AI request failed: ${response.status}`);
const result=await response.json();
console.log("AI analysis response:",result);
handleAIResult(result);
}catch(error){
console.error("AI analysis error:",error);
addAssistantMessage("I could not complete the analysis. Please try again.");
updateMapStatus("Analysis request failed");
}
}

function handleAIResult(result){
if(!result){
addAssistantMessage("No result was returned.");
updateMapStatus("No analysis result");
return;
}
if(result.message)addAssistantMessage(result.message);
if(aiResultLayer){
map.removeLayer(aiResultLayer);
aiResultLayer=null;
}
if(spatialLayers.analysis)delete spatialLayers.analysis;
if(!result.geojson||result.geojson.type!=="FeatureCollection"||!Array.isArray(result.geojson.features)){
updateMapStatus("Analysis complete");
return;
}
if(result.geojson.features.length===0){
updateMapStatus("Analysis complete — no matching features");
return;
}
aiResultLayer=createLeafletLayer("analysis",result.geojson);
aiResultLayer.addTo(map);
spatialLayers.analysis=aiResultLayer;
const bounds=aiResultLayer.getBounds();
if(bounds&&bounds.isValid())map.fitBounds(bounds,{padding:[30,30]});
console.log(`AI analysis: ${result.geojson.features.length} features displayed`);
updateMapStatus("Analysis complete");
}

function clearAIAnalysis(){
if(aiResultLayer){
map.removeLayer(aiResultLayer);
aiResultLayer=null;
}
if(spatialLayers.analysis)delete spatialLayers.analysis;
updateMapStatus("AI analysis cleared");
}

aiToggle?.addEventListener( "click", function () {
        if (!aiPanel) {
            return;
        }

        aiPanel.classList.toggle("open");
    }
);

sendQuestionButton?.addEventListener("click",function(){
if(aiQuestion)askAIQuestion(aiQuestion.value);
});

aiQuestion?.addEventListener("keydown",function(event){
if(event.key==="Enter"&&!event.shiftKey){
event.preventDefault();
askAIQuestion(aiQuestion.value);
}
});

suggestionButtons.forEach(button=>{
button.addEventListener("click",function(){askAIQuestion(button.textContent.trim());});
});

let searchResultLayer=null;

async function performSearch(){
const query=searchInput.value.trim();
if(!query){
updateMapStatus("Enter a location to search.");
return;
}
updateMapStatus(`Searching for "${query}"...`);
try{
const response=await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`);
if(!response.ok)throw new Error(`Search failed with status ${response.status}`);
const geojson=await response.json();
if(!geojson||geojson.type!=="FeatureCollection")throw new Error("Search returned invalid GeoJSON");
if(searchResultLayer){
map.removeLayer(searchResultLayer);
searchResultLayer=null;
}
if(geojson.features.length===0){
updateMapStatus(`No results found for "${query}".`);
return;
}
searchResultLayer=L.geoJSON(geojson,{
style:{weight:4,fillOpacity:.15},
onEachFeature:function(feature,layer){
const properties=feature.properties;
layer.bindPopup(`<strong>${properties.name}</strong><br>Type: ${properties.location_type}<br>${properties.county_name?`County: ${properties.county_name}<br>`:""}${properties.constituency_name?`Constituency: ${properties.constituency_name}<br>`:""}${properties.ward_name?`Ward: ${properties.ward_name}`:""}`);
}
}).addTo(map);
map.fitBounds(searchResultLayer.getBounds(),{padding:[30,30]});
updateMapStatus(`${geojson.features.length} result(s) found`);
}catch(error){
console.error("Search error:",error);
updateMapStatus("Search failed");
}
}

searchButton?.addEventListener("click",performSearch);
searchInput?.addEventListener("keydown",function(event){
if(event.key==="Enter")performSearch();
});

updateMapStatus("Map initialized");