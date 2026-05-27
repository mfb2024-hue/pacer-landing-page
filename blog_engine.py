#!/usr/bin/env python3
"""
PACER Blog Engine v4 — Clean, no syntax errors
21 posts/day (7 per run x 3 runs)
"""

import os, json, time, random, requests, base64, re
from datetime import datetime
from anthropic import Anthropic

GITHUB_REPO  = "mfb2024-hue/pacer-landing-page"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLAUDE_KEY   = os.environ.get("ANTHROPIC_API_KEY")
BLOG_DIR     = "blog"
POSTS_PER_RUN= int(os.environ.get("POSTS_PER_RUN", "7"))
MODEL        = "claude-haiku-4-5-20251001"

client = Anthropic(api_key=CLAUDE_KEY)

# ── CITIES ───────────────────────────────────────────────────────
TIER1 = ["Bangalore","Mumbai","Delhi","Hyderabad","Chennai","Pune","Kolkata"]
TIER2 = ["Ahmedabad","Jaipur","Chandigarh","Kochi","Lucknow","Nagpur","Indore","Coimbatore","Bhubaneswar"]

CITY_COORDS = {
    "Bangalore":"12.9716,77.5946","Mumbai":"19.0760,72.8777",
    "Delhi":"28.6139,77.2090","Hyderabad":"17.3850,78.4867",
    "Chennai":"13.0827,80.2707","Pune":"18.5204,73.8567",
    "Kolkata":"22.5726,88.3639","Ahmedabad":"23.0225,72.5714",
    "Jaipur":"26.9124,75.7873","Chandigarh":"30.7333,76.7794",
    "Kochi":"9.9312,76.2673","Lucknow":"26.8467,80.9462",
    "Nagpur":"21.1458,79.0882","Indore":"22.7196,75.8577",
    "Coimbatore":"11.0168,76.9558","Bhubaneswar":"20.2961,85.8245",
}

CITY_SPOTS = {
    "Bangalore":[("Cubbon Park","12.9763,77.5929","5.8km loop, shaded, best before 7am"),("Lalbagh Garden","12.9507,77.5848","3km loop, flat, opens 6am"),("Ulsoor Lake","12.9815,77.6214","2km loop, central, 5:30-7am"),("Nandi Hills","13.3702,77.6835","Trail runs, cool climate")],
    "Mumbai":[("Marine Drive","18.9322,72.8264","3.6km stretch, sea breeze, best before 7am"),("Carter Road Bandra","19.0728,72.8286","1km promenade, popular 5:30-7am"),("Sanjay Gandhi NP","19.2147,72.9110","Trail running, early morning only"),("Powai Lake","19.1196,72.9089","4km loop, 5:30-7am")],
    "Delhi":[("Lodhi Garden","28.5931,77.2197","2.1km loop, historic, opens 5am"),("Siri Fort","28.5491,77.2226","3km track, well lit, popular"),("Nehru Park","28.5963,77.1940","1.5km loop, shaded, safe"),("India Gate","28.6129,77.2295","Road loop, iconic, early morning only")],
    "Hyderabad":[("KBR National Park","17.4156,78.4347","3km trail, forest cover, opens 5am"),("Hussain Sagar Lake","17.4239,78.4738","5km loop, popular, early morning"),("Necklace Road","17.4126,78.4680","3km stretch, lake views, 5:30-7am"),("Durgam Cheruvu","17.4344,78.3876","Trail loop, rocky terrain, peaceful")],
    "Chennai":[("Marina Beach","13.0500,80.2824","13km stretch, flat, best before 6:30am"),("Besant Nagar Beach","13.0002,80.2707","2km stretch, less crowded"),("Guindy National Park","13.0067,80.2206","Forest trail, opens 8am, shaded"),("Adyar River walk","13.0067,80.2353","Riverside path, quiet morning")],
    "Pune":[("Bund Garden","18.5359,73.8794","1.5km loop, riverside, good track"),("Pune University","18.5590,73.8252","3km perimeter, wide roads, 5-7am"),("Vetal Hill","18.5368,73.8070","Trail, panoramic views, hilly"),("Pashan Lake","18.5424,73.7855","3km loop, peaceful, birding")],
    "Kolkata":[("Maidan","22.5502,88.3451","3km grass loop, central, best before 8am"),("Rabindra Sarobar","22.5142,88.3609","2km lake loop, peaceful, 5-7am"),("Salt Lake","22.5764,88.4249","Wide roads, grid layout, 5:30-7am"),("Victoria Memorial","22.5448,88.3426","1.5km loop, historic, early morning")],
    "Ahmedabad":[("Sabarmati Riverfront","23.0225,72.5714","8km paved path, flat"),("Kankaria Lake","22.9821,72.5955","3km circular, opens 6am"),("Law Garden","23.0258,72.5618","1km loop, night lit"),("ISKCON area","23.0447,72.5274","Quiet roads, wide, morning runners")],
}

# ── TOPICS ───────────────────────────────────────────────────────
CITY_TEMPLATES = [
    "best places to run in {city}",
    "running routes in {city}",
    "where to run in {city} morning",
    "best time to run in {city}",
    "running in {city} summer tips",
    "AQI running conditions {city}",
    "running clubs in {city}",
    "running in {city} monsoon season",
]

GENERIC_TOPICS = [
    "how to start running for beginners","how to start running when unfit",
    "how to start running for weight loss","how to build running stamina from zero",
    "couch to 5K beginner running plan","why is running so hard at first",
    "how to not get breathless while running","how to breathe properly while running",
    "running for beginners week by week plan","how to run 5K for the first time",
    "5K training plan for beginners","10K training plan India",
    "half marathon training plan beginners","marathon training plan India",
    "how to run faster tips","how to increase running distance",
    "what is a tempo run","interval training for runners",
    "zone 2 running what is it","running cadence explained",
    "running for weight loss how much per day","does running reduce belly fat",
    "running 30 minutes a day results","running vs walking for weight loss",
    "how many calories does running burn","running making me gain weight why",
    "best time to run morning or evening","running on empty stomach benefits",
    "what to eat before running","pre run food India",
    "banana before running benefits","sattu for running energy",
    "roti before running good or bad","coconut water during running",
    "post run food India","running diet vegetarian India",
    "hydration tips running India heat","nimbu pani for running",
    "best running shoes India 2026","running shoes for Indian roads",
    "best running shoes under 5000 rupees","running shoes for monsoon India",
    "best running watch India 2026","running earphones wireless India",
    "running tshirt material which is best","running shorts India summer",
    "runners knee symptoms and treatment","shin splints running treatment",
    "IT band syndrome runners fix","plantar fasciitis running cure",
    "how to prevent running injuries","running warm up routine",
    "foam rolling for runners","running cool down stretches",
    "running in Indian summer heat","heat index running India explained",
    "AQI safe levels for running","running in Delhi pollution tips",
    "running in monsoon India 2026","humidity and running performance",
    "best time to run in India summer","heat acclimatisation running India",
    "running app for Indian weather","best running app India 2026",
    "running club management app India","how to start a running club India",
    "running community India online","TCS World 10K training guide",
    "Delhi Half Marathon training plan","Mumbai Marathon training beginner",
    "marathon race day tips India","running motivation how to stay consistent",
    "running habit how to build one","running for mental health India",
    "women running India safety tips","running at night India safety",
    "running and heart health India","running for diabetes India",
    "running benefits for body India","gut issues while running prevention",
    "running form tips India","running posture how to improve",
    "how to run without knee pain","running after 40 India tips",
    "is it safe to run every day","rest days running how many per week",
    "treadmill vs outdoor running India","running in rain good or bad",
    "running blister prevention tips","black toenail runner causes treatment",
]

def all_topics():
    topics = []
    for city in TIER1:
        for t in CITY_TEMPLATES:
            topics.append(t.replace("{city}", city))
    for city in TIER2:
        for t in CITY_TEMPLATES[:5]:
            topics.append(t.replace("{city}", city))
    topics.extend(GENERIC_TOPICS)
    random.shuffle(topics)
    return topics

def slug(topic):
    s = re.sub(r'[^a-z0-9\s-]', '', topic.lower())
    s = re.sub(r'\s+', '-', s.strip())
    return re.sub(r'-+', '-', s).strip('-')[:80]

def detect_city(topic):
    for c in list(CITY_COORDS.keys()):
        if c.lower() in topic.lower():
            return c
    return "Bangalore"

def detect_card(topic):
    t = topic.lower()
    if any(k in t for k in ["food","eat","nutrition","diet","roti","sattu","banana","fuel","meal","carb","protein","nimbu","coconut","curd","idli","dosa","hydrat","electrolyte"]):
        return "food"
    if any(k in t for k in ["training","plan","5k","10k","marathon","coach","interval","pace","speed","cadence","tempo","fartlek","vo2","lactate","beginner","stamina","race","half marathon","build","week","how to run","run faster","run longer"]):
        return "coaching"
    if any(k in t for k in ["where to run","running route","running park","place to run","best place","running track","running spot","running loop"]):
        return "places"
    return "conditions"

def get_existing():
    existing = set()
    try:
        r = requests.get(
            "https://api.github.com/repos/" + GITHUB_REPO + "/contents/" + BLOG_DIR,
            headers={"Authorization": "token " + GITHUB_TOKEN},
            timeout=10
        )
        if r.ok:
            for f in r.json():
                name = f.get("name", "")
                if name.endswith(".html") and name not in ("index.html",):
                    existing.add(name.replace(".html", ""))
    except:
        pass
    return existing

def write_post(topic):
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1600,
        messages=[{"role": "user", "content": (
            'Write a helpful, India-specific blog post for PACER (usepacer.app) about: "' + topic + '"\n\n'
            'PACER is an Indian running intelligence app. It gives Indian runners a daily GO/GO EASY/WAIT/REST verdict '
            'based on live AQI, heat index, and humidity for 300+ Indian cities. Free at usepacer.app.\n\n'
            'CRITICAL LEGAL RULES:\n'
            '- NEVER mention any competitor brand by name (no Strava, Garmin, Nike, Adidas, Apple, Samsung, ASICS, Saucony, Brooks, New Balance, Hoka, Polar, Fitbit, Reebok, Puma)\n'
            '- Use generic terms only: "GPS running apps", "running watches", "sports brands"\n'
            '- NEVER make negative claims about any product or company\n'
            '- Only write factual, verifiable information about running science and conditions\n'
            '- Do not make health promises or specific performance guarantees\n'
            '- Write as general information, not personal advice. Use "research suggests" not "you must"\n\n'
            'CONTENT RULES:\n'
            '- India-specific content. June 2026 onwards where timely.\n'
            '- 700-1000 words\n'
            '- Start with a 2-sentence direct answer\n'
            '- H2 headings written as questions\n'
            '- FAQ section at end with 4 Q&As\n'
            '- Mention PACER 2-3 times where it fits naturally\n'
            '- End with exactly: Check today\'s conditions at [usepacer.app](https://usepacer.app) - free.\n'
            '- Clean Markdown. No fluff. Every sentence must be useful.'
        )}]
    )
    return msg.content[0].text

def food_card_html():
    return (
        '<div style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:16px">PACER · PRE-RUN FUEL GUIDE</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px">'
        '<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:14px;text-align:center">'
        '<div style="font-size:11px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">2 HRS BEFORE</div>'
        '<div style="font-size:13px;color:#fff;font-weight:600;line-height:1.6">Curd rice<br>Idli / Dosa<br>Dal + rice</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:14px;text-align:center">'
        '<div style="font-size:11px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">30 MIN BEFORE</div>'
        '<div style="font-size:13px;color:#fff;font-weight:600;line-height:1.6">Banana<br>2-3 Dates<br>Sattu drink</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:14px;text-align:center">'
        '<div style="font-size:11px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">AFTER RUN</div>'
        '<div style="font-size:13px;color:#fff;font-weight:600;line-height:1.6">Dal + rice<br>Curd + banana<br>Chaas</div>'
        '</div></div>'
        '<div style="background:rgba(255,255,255,.03);border-radius:8px;padding:12px;margin-bottom:16px;font-size:13px;color:#666;line-height:1.6">'
        '<strong style="color:#aaa">Tip:</strong> In Indian heat your body needs more electrolytes. PACER tells you conditions before you step out so you fuel for the actual day, not a plan made for London.'
        '</div>'
        '<a href="https://usepacer.app" style="display:block;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">Check today\'s conditions and adjust your fuel plan</a>'
        '</div>'
    )

def coaching_card_html():
    return (
        '<div style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:16px">PACER · SMART EFFORT GUIDE</div>'
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:20px">'
        '<div style="background:rgba(74,222,128,.07);border:1px solid rgba(74,222,128,.2);border-radius:10px;padding:12px;text-align:center">'
        '<div style="font-size:15px;font-weight:900;color:#4ade80;margin-bottom:4px">GO</div>'
        '<div style="font-size:11px;color:#555">Full effort ok today</div></div>'
        '<div style="background:rgba(163,230,53,.07);border:1px solid rgba(163,230,53,.2);border-radius:10px;padding:12px;text-align:center">'
        '<div style="font-size:11px;font-weight:900;color:#A3E635;margin-bottom:4px">GO EASY</div>'
        '<div style="font-size:11px;color:#555">Reduce intensity</div></div>'
        '<div style="background:rgba(255,149,0,.07);border:1px solid rgba(255,149,0,.2);border-radius:10px;padding:12px;text-align:center">'
        '<div style="font-size:15px;font-weight:900;color:#FF9500;margin-bottom:4px">WAIT</div>'
        '<div style="font-size:11px;color:#555">Short run only</div></div>'
        '<div style="background:rgba(255,68,68,.07);border:1px solid rgba(255,68,68,.2);border-radius:10px;padding:12px;text-align:center">'
        '<div style="font-size:15px;font-weight:900;color:#ff4444;margin-bottom:4px">REST</div>'
        '<div style="font-size:11px;color:#555">Skip. Train inside</div></div></div>'
        '<div style="background:rgba(255,255,255,.03);border-radius:8px;padding:12px;margin-bottom:16px;font-size:13px;color:#666;line-height:1.6">'
        '<strong style="color:#aaa">Every training plan assumes ideal conditions.</strong> In Indian heat, humidity, and monsoon, PACER reads live AQI and gives you one verdict before you head out.'
        '</div>'
        '<a href="https://usepacer.app" style="display:block;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">See today\'s training verdict for your city</a>'
        '</div>'
    )

def places_card_html(city):
    spots = CITY_SPOTS.get(city, CITY_SPOTS["Bangalore"])
    rows = ""
    for name, coords, desc in spots:
        maps_url = "https://www.google.com/maps/search/?api=1&query=" + coords
        rows += (
            '<div style="display:flex;align-items:flex-start;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05);gap:12px">'
            '<div><div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:3px">' + name + '</div>'
            '<div style="font-size:12px;color:#555">' + desc + '</div></div>'
            '<a href="' + maps_url + '" target="_blank" rel="noopener" style="background:rgba(79,159,255,.1);border:1px solid rgba(79,159,255,.2);color:#4F9FFF;padding:6px 12px;border-radius:7px;font-size:11px;font-weight:600;text-decoration:none;white-space:nowrap;flex-shrink:0">Maps</a>'
            '</div>'
        )
    return (
        '<div style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:4px">PACER · TOP RUNNING SPOTS</div>'
        '<div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:16px">' + city + '</div>'
        + rows +
        '<div style="margin-top:16px;background:rgba(255,255,255,.03);border-radius:8px;padding:12px;font-size:13px;color:#666;line-height:1.6">'
        'Check AQI and heat before heading out. <strong style="color:#aaa">PACER</strong> gives you a GO/WAIT verdict every morning.'
        '</div>'
        '<a href="https://usepacer.app" style="display:block;margin-top:14px;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">Check today\'s conditions in ' + city + '</a>'
        '</div>'
    )

def conditions_widget_html(city):
    coords = CITY_COORDS.get(city, "12.9716,77.5946").split(",")
    lat, lon = coords[0], coords[1]
    owm = "b6907d289e10d714a6e88b30761fdd59"
    return (
        '<div id="pw" style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:16px">PACER · LIVE CONDITIONS · ' + city.upper() + '</div>'
        '<div id="pw-l" style="color:#555;font-size:14px">Loading conditions...</div>'
        '<div id="pw-c" style="display:none">'
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:18px">'
        '<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:12px;text-align:center"><div id="pw-aqi" style="font-size:22px;font-weight:800;color:#fff"></div><div style="font-size:10px;color:#555;margin-top:2px;letter-spacing:1px">AQI</div></div>'
        '<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:12px;text-align:center"><div id="pw-hi" style="font-size:22px;font-weight:800;color:#fff"></div><div style="font-size:10px;color:#555;margin-top:2px;letter-spacing:1px">HEAT INDEX</div></div>'
        '<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:12px;text-align:center"><div id="pw-hum" style="font-size:22px;font-weight:800;color:#fff"></div><div style="font-size:10px;color:#555;margin-top:2px;letter-spacing:1px">HUMIDITY</div></div>'
        '</div>'
        '<div id="pw-v" style="border-radius:8px;padding:12px;margin-bottom:16px;display:flex;align-items:center;gap:12px">'
        '<div id="pw-vt" style="font-size:18px;font-weight:900;letter-spacing:1px"></div>'
        '<div id="pw-vm" style="font-size:13px;color:#777"></div>'
        '</div>'
        '<a href="https://usepacer.app" style="display:block;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">Get this every morning for your city</a>'
        '</div>'
        '<div id="pw-e" style="display:none;font-size:13px;color:#555">Check live conditions at <a href="https://usepacer.app" style="color:#4F9FFF">usepacer.app</a></div>'
        '</div>'
        '<script>'
        '(function(){'
        'var K="' + owm + '",lat=' + lat + ',lon=' + lon + ';'
        'function hi(t,h){var F=t*9/5+32;return Math.round((-42.379+2.049*F+10.143*h-0.225*F*h-0.007*F*F-0.055*h*h+0.001*F*F*h+0.001*F*h*h-32)*5/9);}'
        'function vrd(a,h){if(a>200||h>44)return{t:"REST",bg:"rgba(255,68,68,.1)",c:"#ff4444",m:"Not recommended. AQI or heat too high. Rest or train indoors."};'
        'if(a>150||h>39)return{t:"WAIT",bg:"rgba(255,149,0,.1)",c:"#FF9500",m:"Tough conditions. Keep it very short and easy."};'
        'if(a>100||h>34)return{t:"GO EASY",bg:"rgba(163,230,53,.1)",c:"#A3E635",m:"Doable but warm. Run at easy effort. Hydrate well."};'
        'return{t:"GO",bg:"rgba(74,222,128,.1)",c:"#4ade80",m:"Good conditions. AQI safe, heat manageable. Good run."};}'
        'Promise.all([fetch("https://api.openweathermap.org/data/2.5/weather?lat="+lat+"&lon="+lon+"&units=metric&appid="+K),'
        'fetch("https://api.openweathermap.org/data/2.5/air_pollution?lat="+lat+"&lon="+lon+"&appid="+K)])'
        '.then(function(r){return Promise.all([r[0].json(),r[1].json()])})'
        '.then(function(d){'
        'var t=Math.round(d[0].main.temp),h=Math.round(d[0].main.humidity),heat=hi(t,h),aqi=d[1].list[0].main.aqi*50,v=vrd(aqi,heat);'
        'document.getElementById("pw-aqi").textContent=aqi;'
        'document.getElementById("pw-hi").textContent=heat+"°C";'
        'document.getElementById("pw-hum").textContent=h+"%";'
        'var vd=document.getElementById("pw-v");vd.style.background=v.bg;vd.style.border="1px solid "+v.c+"40";'
        'document.getElementById("pw-vt").textContent=v.t;document.getElementById("pw-vt").style.color=v.c;'
        'document.getElementById("pw-vm").textContent=v.m;'
        'document.getElementById("pw-l").style.display="none";document.getElementById("pw-c").style.display="block";'
        '}).catch(function(){document.getElementById("pw-l").style.display="none";document.getElementById("pw-e").style.display="block";});'
        '})();'
        '</script>'
    )

def get_contextual_card(topic):
    card_type = detect_card(topic)
    city = detect_city(topic)
    if card_type == "food":     return food_card_html()
    if card_type == "coaching": return coaching_card_html()
    if card_type == "places":   return places_card_html(city)
    return conditions_widget_html(city)

CONVERSION_STRIP = (
    '<div style="background:rgba(79,159,255,.07);border:1px solid rgba(79,159,255,.15);border-radius:12px;padding:20px 22px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">'
    '<div><div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:3px">Check today\'s running conditions</div>'
    '<div style="font-size:12px;color:#666">Live AQI · Heat index · GO/WAIT verdict for your city</div></div>'
    '<a href="https://usepacer.app" style="background:#4F9FFF;color:#000;padding:10px 20px;border-radius:8px;font-weight:700;font-size:12px;text-decoration:none;white-space:nowrap;flex-shrink:0">Open PACER free</a>'
    '</div>'
)

STICKY_BAR = (
    '<div id="psb" style="position:fixed;bottom:0;left:0;right:0;background:#0d0d0d;border-top:1px solid rgba(79,159,255,.2);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;z-index:999;transform:translateY(100%);transition:transform .4s ease">'
    '<div><div style="font-size:13px;font-weight:700;color:#fff">PACER — Running Intelligence for India</div>'
    '<div style="font-size:11px;color:#555;margin-top:1px">Free. Live AQI + conditions for your city.</div></div>'
    '<a href="https://usepacer.app" style="background:#4F9FFF;color:#000;padding:9px 18px;border-radius:8px;font-weight:700;font-size:12px;text-decoration:none;flex-shrink:0">Try free</a>'
    '</div>'
    '<script>'
    'setTimeout(function(){var b=document.getElementById("psb");if(b)b.style.transform="translateY(0)"},4000);'
    'window.addEventListener("scroll",function(){var b=document.getElementById("psb");if(!b)return;'
    'if((window.scrollY/(document.body.scrollHeight-window.innerHeight))*100>25)b.style.transform="translateY(0)";});'
    '</script>'
)

DISCLAIMER = (
    '<div style="margin-top:48px;padding:20px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px;font-size:12px;color:#444;line-height:1.7">'
    '<strong style="color:#555;display:block;margin-bottom:6px">Disclaimer</strong>'
    'This article is for general informational purposes only. All information is sourced from publicly available research and general knowledge. '
    'It does not constitute medical, fitness, or professional advice. Always consult a qualified professional before making changes to your exercise routine or acting on health information. '
    'PACER and its team accept no liability for any outcome arising from use of this information. '
    'Running conditions shown on usepacer.app are sourced from third-party APIs and provided as-is without warranty of accuracy.'
    '</div>'
)

def md_to_html(md):
    h = md
    h = re.sub(r'^### (.+)$', r'<h3>\1</h3>', h, flags=re.MULTILINE)
    h = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', h, flags=re.MULTILINE)
    h = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', h, flags=re.MULTILINE)
    h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
    h = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', h)
    h = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', h)
    h = h.replace('\n---\n', '\n<hr>\n')
    out = []
    for line in h.split('\n'):
        l = line.strip()
        if not l:             out.append('')
        elif l.startswith('<'): out.append(l)
        elif l.startswith('- ') or l.startswith('* '): out.append('<li>' + l[2:] + '</li>')
        else:                  out.append('<p>' + l + '</p>')
    return '\n'.join(out)

def build_html(md, topic):
    title = topic.title()
    m = re.search(r'<h1>(.+?)</h1>', md_to_html(md))
    if m: title = m.group(1)
    meta = "PACER guide: " + topic + ". Indian running intelligence for AQI, heat, and conditions."
    date = datetime.now().strftime("%B %d, %Y")
    body = md_to_html(md)
    lines = body.split('\n')
    split = max(6, len(lines) // 2)
    top_body = '\n'.join(lines[:split])
    bot_body = '\n'.join(lines[split:])
    card = get_contextual_card(topic)
    schema = '{"@context":"https://schema.org","@type":"Article","headline":"' + title + '","datePublished":"' + datetime.now().isoformat() + '","publisher":{"@type":"Organization","name":"PACER","url":"https://usepacer.app"},"description":"' + meta + '"}'
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>\n'
        '<title>' + title + ' | PACER</title>\n'
        '<meta name="description" content="' + meta + '"/>\n'
        '<script type="application/ld+json">' + schema + '</script>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet"/>\n'
        '<style>\n'
        '*{box-sizing:border-box;margin:0;padding:0}\n'
        'body{font-family:"Inter",system-ui,sans-serif;background:#000;color:#ddd;line-height:1.75;-webkit-font-smoothing:antialiased;padding-bottom:80px}\n'
        'nav{position:sticky;top:0;background:rgba(0,0,0,.92);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.08);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;z-index:100}\n'
        '.nb{font-size:15px;font-weight:700;color:#fff;text-decoration:none}\n'
        '.nc{background:#4F9FFF;color:#000;border-radius:7px;padding:7px 16px;font-size:12px;font-weight:700;text-decoration:none}\n'
        '.wrap{max-width:720px;margin:0 auto;padding:48px 24px 64px}\n'
        '.meta{font-size:11px;color:#444;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px}\n'
        'h1{font-size:clamp(24px,5vw,40px);font-weight:800;letter-spacing:-1.5px;line-height:1.1;color:#fff;margin-bottom:20px}\n'
        'h2{font-size:22px;font-weight:700;color:#fff;margin:36px 0 12px}\n'
        'h3{font-size:17px;font-weight:600;color:#ccc;margin:24px 0 8px}\n'
        'p{color:#999;margin-bottom:16px;font-size:15px;font-weight:300}\n'
        'li{color:#999;margin-bottom:8px;font-size:15px;margin-left:22px}\n'
        'strong{color:#ddd;font-weight:600}\n'
        'em{color:#bbb}\n'
        'a{color:#4F9FFF;text-decoration:none}\n'
        'a:hover{text-decoration:underline}\n'
        'hr{border:none;border-top:1px solid rgba(255,255,255,.07);margin:32px 0}\n'
        '.back{display:block;margin-top:40px;font-size:13px;color:#444}\n'
        '.back a{color:#4F9FFF}\n'
        '</style>\n</head>\n<body>\n'
        '<nav><a href="https://usepacer.app" class="nb">PACER</a>'
        '<a href="https://usepacer.app" class="nc">Early access</a></nav>\n'
        '<div class="wrap">\n'
        '<p class="meta">PACER · INDIAN RUNNING INTELLIGENCE · ' + date + '</p>\n'
        + top_body + '\n'
        + card + '\n'
        + CONVERSION_STRIP + '\n'
        + bot_body + '\n'
        + '<p class="back">Back to <a href="https://usepacer.app/blog">all running guides</a> &middot; <a href="https://usepacer.app">usepacer.app</a></p>\n'
        + DISCLAIMER + '\n'
        '</div>\n'
        + STICKY_BAR + '\n'
        '</body></html>'
    )

def push(filename, content, msg):
    url = "https://api.github.com/repos/" + GITHUB_REPO + "/contents/" + BLOG_DIR + "/" + filename
    hdrs = {"Authorization": "token " + GITHUB_TOKEN}
    sha = None
    r = requests.get(url, headers=hdrs, timeout=8)
    if r.ok: sha = r.json().get("sha")
    payload = {"message": msg, "content": base64.b64encode(content.encode()).decode()}
    if sha: payload["sha"] = sha
    r = requests.put(url, headers=hdrs, json=payload, timeout=15)
    return r.status_code in (200, 201)

def update_index(entries):
    items = "\n".join('<li><a href="' + s + '.html">' + t + '</a></li>' for s, t in entries[:500])
    html = (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
        '<title>PACER Running Guides - India</title>'
        '<meta name="description" content="Running guides for Indian runners. AQI, heat, monsoon, routes, nutrition - written for real Indian runners."/>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet"/>'
        '<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:"Inter",system-ui,sans-serif;background:#000;color:#ddd;-webkit-font-smoothing:antialiased}'
        'nav{position:sticky;top:0;background:rgba(0,0,0,.92);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.08);padding:14px 24px;display:flex;align-items:center;justify-content:space-between}'
        '.nb{font-size:15px;font-weight:700;color:#fff;text-decoration:none}.nc{background:#4F9FFF;color:#000;border-radius:7px;padding:7px 16px;font-size:12px;font-weight:700;text-decoration:none}'
        '.wrap{max-width:720px;margin:0 auto;padding:48px 24px 96px}'
        'h1{font-size:clamp(22px,5vw,36px);font-weight:800;letter-spacing:-1.5px;color:#fff;margin-bottom:8px}'
        '.sub{color:#555;font-size:15px;font-weight:300;margin-bottom:36px}'
        'ul{list-style:none}li{border-bottom:1px solid rgba(255,255,255,.05);padding:13px 0}li:last-child{border-bottom:none}'
        'a{color:#4F9FFF;text-decoration:none;font-size:15px}a:hover{text-decoration:underline}</style>'
        '</head><body>'
        '<nav><a href="https://usepacer.app" class="nb">PACER</a><a href="https://usepacer.app" class="nc">Early access</a></nav>'
        '<div class="wrap">'
        '<h1>Running Guides for India</h1>'
        '<p class="sub">AQI, heat, monsoon, nutrition, routes - written for real Indian runners.</p>'
        '<ul>' + items + '</ul>'
        '</div></body></html>'
    )
    push("index.html", html, "Update blog index - " + str(len(entries)) + " posts")

def update_log(new_entries):
    url = "https://api.github.com/repos/" + GITHUB_REPO + "/contents/" + BLOG_DIR + "/published.json"
    hdrs = {"Authorization": "token " + GITHUB_TOKEN}
    log = []
    sha = None
    r = requests.get(url, headers=hdrs, timeout=8)
    if r.ok:
        sha = r.json().get("sha")
        try: log = json.loads(base64.b64decode(r.json()["content"]).decode())
        except: pass
    existing_slugs = {e["slug"] for e in log}
    for s, t in new_entries:
        if s not in existing_slugs:
            log.append({"slug": s, "title": t, "date": datetime.now().strftime("%Y-%m-%d"), "url": "https://usepacer.app/blog/" + s + ".html"})
    payload = {"message": "Log: " + str(len(new_entries)) + " new posts", "content": base64.b64encode(json.dumps(log, indent=2).encode()).decode()}
    if sha: payload["sha"] = sha
    requests.put(url, headers=hdrs, json=payload, timeout=15)

def run():
    print("=== PACER Blog Engine v4 - " + str(POSTS_PER_RUN) + " posts - " + datetime.now().strftime("%Y-%m-%d %H:%M") + " ===")
    if not GITHUB_TOKEN or not CLAUDE_KEY:
        print("ERROR: Missing GITHUB_TOKEN or ANTHROPIC_API_KEY")
        return

    existing = get_existing()
    print("Existing posts: " + str(len(existing)))

    topics = all_topics()
    queue = []
    seen = set()
    for t in topics:
        s = slug(t)
        if s not in existing and s not in seen:
            queue.append(t)
            seen.add(s)
        if len(queue) >= POSTS_PER_RUN:
            break

    print("Writing " + str(len(queue)) + " posts...")
    new_entries = []

    for i, topic in enumerate(queue, 1):
        s = slug(topic)
        print("[" + str(i) + "/" + str(len(queue)) + "] " + topic[:60])
        try:
            md = write_post(topic)
            html = build_html(md, topic)
            title_m = re.search(r'<h1>(.+?)</h1>', html)
            title = title_m.group(1) if title_m else topic.title()
            ok = push(s + ".html", html, "blog: " + topic[:55])
            if ok:
                new_entries.append((s, title))
                existing.add(s)
                print("  published")
            else:
                print("  push failed")
            time.sleep(2)
        except Exception as e:
            print("  error: " + str(e))

    if new_entries:
        all_e = [(s, t) for s, t in new_entries] + [(s, s.replace('-', ' ').title()) for s in existing if s not in {e[0] for e in new_entries}]
        update_index(all_e)
        update_log(new_entries)

    print("\n=== Done. " + str(len(new_entries)) + " new posts published. ===")

if __name__ == "__main__":
    run()
# and Reddit/Quora research — NOT guesses.

CITY_TEMPLATES = [
    # Where to run — high intent, local searches
    "best places to run in {city}",
    "running routes in {city}",
    "where to run in {city} morning",
    "best running parks in {city}",

    # Conditions — PACER's core value
    "best time to run in {city}",
    "running in {city} summer tips",
    "AQI running {city}",
    "air quality running {city}",
    "running in {city} monsoon season",
    "running in {city} heat humidity",

    # Events — high search volume around race season
    "running clubs in {city}",
    "running events in {city} 2025",
    "marathons in {city} 2025 2026",
    "half marathon training {city}",
    "how to prepare for {city} marathon",
    "5K run {city}",
    "running group {city}",
]

GENERIC_INDIA_TOPICS = [
    # Conditions — PACER's exact use case
    "is it safe to run in high AQI India",
    "AQI levels safe for running India",
    "running in Delhi pollution tips",
    "running with mask India AQI",
    "best time to run morning India",
    "running in summer heat India",
    "running heat stroke prevention India",
    "heat index running India explained",
    "running in monsoon India tips",
    "monsoon running gear India",
    "humidity running India performance",

    # Training — Indians actually search these
    "how to start running India beginner",
    "beginner running plan India",
    "how to run 5K India first time",
    "10K training plan India",
    "half marathon training plan India",
    "marathon training for Indian runners",
    "how to improve running pace India",
    "running cadence improvement India",
    "running form tips India",
    "interval training running India",
    "how to run without stopping India",
    "running vs walking weight loss India",

    # Nutrition — huge gap, Indians searching this
    "what to eat before morning run India",
    "pre run food Indian diet",
    "sattu for running energy",
    "roti before running good or bad",
    "banana before running India",
    "coconut water running India",
    "post run food Indian diet",
    "running diet plan vegetarian India",
    "hydration tips running India heat",
    "electrolytes running India natural",
    "nimbu pani running India",

    # Gear — high volume searches
    "best running shoes India under 5000",
    "best running shoes India 2025",
    "running shoes for Indian roads",
    "Nike running shoes India review",
    "Adidas running shoes India",
    "ASICS running shoes India",
    "running shoes monsoon India",
    "best running watch India",
    "Garmin watch India runner review",
    "running earphones India",
    "running tshirt India summer",
    "running shorts India",

    # Injury — people search when hurting
    "runners knee treatment India",
    "shin splints running India",
    "how to prevent running injuries India",
    "running blister prevention India",
    "IT band pain running India",
    "plantar fasciitis runners India",
    "running ankle pain India",

    # PACER feature-related — direct
    "running app for Indian weather",
    "running app with AQI India",
    "best running app India 2025",
    "running app for heat and humidity India",
    "running club management app India",
    "how to manage running club India",
    "run club attendance tracking India",
    "running event app India",
    "running coach app India",

    # Races — event-specific high search volume
    "TCS World 10K Bangalore training guide",
    "Airtel Delhi Half Marathon training",
    "Mumbai Marathon training plan beginner",
    "Pune Marathon preparation guide",
    "Bengaluru Marathon training tips",
    "how to qualify for Mumbai Marathon",
    "Delhi Half Marathon AQI running",
    "marathon pace strategy India",
    "race day tips marathon India",
    "running bib collection India",

    # Social / Motivation
    "how to stay motivated running India",
    "running community India online",
    "running alone vs running club India",
    "benefits of running India health",
    "running for mental health India",
    "women running India safety tips",
    "running at night India safety",
    "running early morning India benefits",
]

def all_topics():
    """Return all unique topics in smart priority order."""
    topics = []
    # City-specific first (high local intent, less competition)
    for city in TIER1:
        for t in CITY_TEMPLATES:
            topics.append(t.replace("{city}", city))
    for city in TIER2:
        for t in CITY_TEMPLATES[:8]:  # fewer templates for tier 2
            topics.append(t.replace("{city}", city))
    # Generic India topics
    topics.extend(GENERIC_INDIA_TOPICS)
    return topics


def get_live_trending():
    """Pull real-time suggestions from Google for Indian running searches."""
    seeds = [
        "running in India",
        "running app India",
        "marathon India 2025",
        "running Bangalore",
        "running Mumbai",
        "running Delhi pollution",
        "AQI run",
        "running heat India",
        "best running shoes India",
    ]
    live = []
    for q in seeds:
        try:
            r = requests.get(
                "https://suggestqueries.google.com/complete/search",
                params={"client":"firefox","q":q,"hl":"en-IN","gl":"in"},
                headers={"User-Agent":"Mozilla/5.0"},
                timeout=5
            )
            if r.ok:
                live.extend(r.json()[1][:3])
            time.sleep(0.3)
        except: pass
    return live


def slug(topic):
    s = re.sub(r'[^a-z0-9\s-]','', topic.lower())
    s = re.sub(r'\s+','-',s.strip())
    return re.sub(r'-+','-',s).strip('-')[:80]


def get_existing():
    """Returns set of already-published slugs. Checks GitHub file listing."""
    existing = set()
    try:
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{BLOG_DIR}",
            headers={"Authorization":f"token {GITHUB_TOKEN}"},
            timeout=10
        )
        if r.ok:
            for f in r.json():
                name = f.get("name","")
                if name.endswith(".html") and name not in ("index.html","sitemap.xml"):
                    existing.add(name.replace(".html",""))
    except: pass
    return existing

def update_published_log(new_entries):
    """Maintain blog/published.json — human-readable log of all published posts."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{BLOG_DIR}/published.json"
    hdrs = {"Authorization":f"token {GITHUB_TOKEN}"}
    existing_log = []
    sha = None
    r = requests.get(url, headers=hdrs, timeout=8)
    if r.ok:
        sha = r.json().get("sha")
        try:
            existing_log = json.loads(base64.b64decode(r.json()["content"]).decode())
        except: pass
    # Merge
    existing_slugs = {e["slug"] for e in existing_log}
    for slug, title in new_entries:
        if slug not in existing_slugs:
            existing_log.append({
                "slug": slug,
                "title": title,
                "published": datetime.now().strftime("%Y-%m-%d"),
                "url": f"https://usepacer.app/blog/{slug}.html"
            })
    content = json.dumps(existing_log, indent=2, ensure_ascii=False)
    payload = {"message": f"Log: {len(new_entries)} new posts",
               "content": base64.b64encode(content.encode()).decode()}
    if sha: payload["sha"] = sha
    requests.put(url, headers=hdrs, json=payload, timeout=15)


def write_post(topic):
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1600,
        messages=[{"role":"user","content":f"""Write a helpful, India-specific blog post for PACER (usepacer.app) about: "{topic}"

PACER is an Indian running intelligence app. It gives Indian runners a daily GO/GO EASY/WAIT/REST verdict based on live AQI, heat index, and humidity for 300+ cities. Free. Built for India.

CRITICAL LEGAL RULES — follow strictly:
- NEVER mention any competitor brand by name (Strava, Garmin, Nike, Adidas, Apple, Samsung, ASICS, Saucony, Brooks, New Balance, Hoka, Polar, Fitbit, Reebok, Puma, Under Armour, GU, etc.)
- Instead use generic terms: "GPS running apps", "running watches", "energy gels", "sports brands"
- NEVER make negative claims about any product or company
- NEVER compare PACER to named competitors
- Only write factual, verifiable information about running science, training, nutrition, and conditions
- Do not make health claims that require medical backing ("running cures X disease")
- Do not make specific performance promises ("you will lose X kg in Y days")

CONTENT RULES:
- India-specific content only. June 2026 onwards where timely.
- Real, useful information for Indian runners.
- 700-1000 words.
- Start with a 2-sentence direct answer to the topic.
- Use H2 headings written as questions.
- Include an FAQ section (4 Q&As) at the end.
- Mention PACER 2-3 times where it genuinely fits — not forced.
- End with this exact line: Check today's conditions at [usepacer.app](https://usepacer.app) — free.
- Clean Markdown format.
- No fluff, no padding. Every sentence must be useful.
- Do not write as if giving personal medical or training advice. Write as general information only.
- Do not use phrases like "you should" or "you must" for health decisions. Use "research suggests" or "many runners find that"."""}]
    )
    return msg.content[0].text


def to_html(md, topic):
    title = topic.title()
    m = re.search(r'^# (.+)$', md, re.MULTILINE)
    if m: title = m.group(1)
    meta = f"PACER — {topic}. Indian running guide for AQI, heat, conditions."

    body = md
    body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', body, flags=re.MULTILINE)
    body = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', body, flags=re.MULTILINE)
    body = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', body, flags=re.MULTILINE)
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    body = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', body)
    body = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', body)
    body = body.replace('\n---\n', '\n<hr>\n')

    out = []
    for line in body.split('\n'):
        l = line.strip()
        if not l:             out.append('')
        elif l.startswith('<'):out.append(l)
        elif l.startswith('- ') or l.startswith('* '): out.append(f'<li>{l[2:]}</li>')
        else:                  out.append(f'<p>{l}</p>')

    # Inject live widget for city-specific or generic posts
    city      = detect_city(topic)
    widget    = WIDGET_SCRIPT.replace('{CITY}', city) if detect_card_type(topic) == 'conditions' else ''
    topic_card = get_card(topic)  # food / coaching / places / or empty (conditions uses widget)

    date = datetime.now().strftime("%B %d, %Y")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title} | PACER</title>
<meta name="description" content="{meta}"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet"/>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article",
"headline":"{title}","datePublished":"{datetime.now().isoformat()}",
"publisher":{{"@type":"Organization","name":"PACER","url":"https://usepacer.app"}},
"description":"{meta}"}}
</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:#000;color:#ddd;line-height:1.75;-webkit-font-smoothing:antialiased}}
nav{{position:sticky;top:0;background:rgba(0,0,0,.92);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.08);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;z-index:100}}
.nb{{font-size:15px;font-weight:700;color:#fff;text-decoration:none}}
.nc{{background:#4F9FFF;color:#000;border-radius:7px;padding:7px 16px;font-size:12px;font-weight:700;text-decoration:none}}
.wrap{{max-width:720px;margin:0 auto;padding:48px 24px 96px}}
.meta{{font-size:11px;color:#444;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px}}
h1{{font-size:clamp(24px,5vw,40px);font-weight:800;letter-spacing:-1.5px;line-height:1.1;color:#fff;margin-bottom:20px}}
h2{{font-size:22px;font-weight:700;color:#fff;margin:36px 0 12px}}
h3{{font-size:17px;font-weight:600;color:#ccc;margin:24px 0 8px}}
p{{color:#999;margin-bottom:16px;font-size:15px;font-weight:300}}
li{{color:#999;margin-bottom:8px;font-size:15px;margin-left:22px}}
strong{{color:#ddd;font-weight:600}}
a{{color:#4F9FFF;text-decoration:none}}a:hover{{text-decoration:underline}}
hr{{border:none;border-top:1px solid rgba(255,255,255,.07);margin:32px 0}}
.back{{display:block;margin-top:40px;font-size:13px;color:#444}}
.back a{{color:#4F9FFF}}
</style>
</head>
<body>
<nav><a href="https://usepacer.app" class="nb">PACER</a>
<a href="https://usepacer.app" class="nc">Early access</a></nav>
<div class="wrap">
<p class="meta">PACER · Indian Running Intelligence · {date}</p>
{chr(10).join(out[:max(6, len(out)//2)])}
{widget}

<div style="background:rgba(79,159,255,.07);border:1px solid rgba(79,159,255,.15);border-radius:12px;padding:20px 22px;margin:32px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
  <div>
    <div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:3px">Check today's running conditions</div>
    <div style="font-size:12px;color:#666">Live AQI · Heat index · GO/WAIT verdict for your city</div>
  </div>
  <a href="https://usepacer.app" style="background:#4F9FFF;color:#000;padding:10px 20px;border-radius:8px;font-weight:700;font-size:12px;text-decoration:none;white-space:nowrap;flex-shrink:0">Open PACER — free →</a>
</div>
{chr(10).join(out[max(6, len(out)//2):])}
<p class="back">← <a href="https://usepacer.app/blog">All running guides</a> · <a href="https://usepacer.app">usepacer.app</a></p>

<div style="margin-top:48px;padding:20px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px;font-size:12px;color:#444;line-height:1.7">
<strong style="color:#555;display:block;margin-bottom:6px">Disclaimer</strong>
This article is for general informational purposes only. All information is sourced from publicly available research, studies, and general knowledge. It does not constitute medical, fitness, or professional advice of any kind. Individual results and experiences may vary. Always consult a qualified medical professional or certified fitness coach before starting any new exercise programme, making changes to your training, or acting on health-related information. PACER, its team, and its affiliates accept no liability for any loss, injury, or outcome arising from the use of information in this article. Running conditions data shown on usepacer.app is sourced from third-party weather and air quality APIs and is provided as-is without warranty of accuracy or completeness.
</div>
</div>

<div id="pacer-sticky" style="position:fixed;bottom:0;left:0;right:0;background:#0d0d0d;border-top:1px solid rgba(79,159,255,.2);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;z-index:999;transform:translateY(100%);transition:transform .4s ease">
  <div>
    <div style="font-size:13px;font-weight:700;color:#fff">PACER — Running Intelligence for India</div>
    <div style="font-size:11px;color:#555;margin-top:1px">Free. Live AQI + conditions for your city.</div>
  </div>
  <a href="https://usepacer.app" style="background:#4F9FFF;color:#000;padding:9px 18px;border-radius:8px;font-weight:700;font-size:12px;text-decoration:none;flex-shrink:0">Try free →</a>
</div>
<script>
setTimeout(function(){
  var bar = document.getElementById('pacer-sticky');
  if(bar) bar.style.transform = 'translateY(0)';
}, 4000);
window.addEventListener('scroll', function(){
  var bar = document.getElementById('pacer-sticky');
  if(!bar) return;
  var scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
  if(scrolled > 25) bar.style.transform = 'translateY(0)';
});
</script>
</body></html>"""


def push(filename, content, msg):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{BLOG_DIR}/{filename}"
    hdrs = {"Authorization":f"token {GITHUB_TOKEN}"}
    sha = None
    r = requests.get(url, headers=hdrs, timeout=8)
    if r.ok: sha = r.json().get("sha")
    payload = {"message":msg, "content":base64.b64encode(content.encode()).decode()}
    if sha: payload["sha"] = sha
    r = requests.put(url, headers=hdrs, json=payload, timeout=15)
    return r.status_code in (200,201)


def update_index(entries):
    items = "\n".join(
        f'<li><a href="{s}.html">{t}</a></li>' for s,t in entries[:300]
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>PACER Running Guides — India</title>
<meta name="description" content="Running guides for Indian runners. AQI, heat, monsoon, routes, nutrition, training — for Bangalore, Mumbai, Delhi and every Indian city."/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:#000;color:#ddd;-webkit-font-smoothing:antialiased}}
nav{{position:sticky;top:0;background:rgba(0,0,0,.92);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.08);padding:14px 24px;display:flex;align-items:center;justify-content:space-between}}
.nb{{font-size:15px;font-weight:700;color:#fff;text-decoration:none}}
.nc{{background:#4F9FFF;color:#000;border-radius:7px;padding:7px 16px;font-size:12px;font-weight:700;text-decoration:none}}
.wrap{{max-width:720px;margin:0 auto;padding:48px 24px 96px}}
h1{{font-size:clamp(22px,5vw,36px);font-weight:800;letter-spacing:-1.5px;color:#fff;margin-bottom:8px}}
.sub{{color:#555;font-size:15px;font-weight:300;margin-bottom:36px}}
ul{{list-style:none}}
li{{border-bottom:1px solid rgba(255,255,255,.05);padding:13px 0}}
li:last-child{{border-bottom:none}}
a{{color:#4F9FFF;text-decoration:none;font-size:15px}}
a:hover{{text-decoration:underline}}
</style>
</head>
<body>
<nav><a href="https://usepacer.app" class="nb">PACER</a>
<a href="https://usepacer.app" class="nc">Early access</a></nav>
<div class="wrap">
<h1>Running Guides for India</h1>
<p class="sub">AQI, heat, monsoon, routes, nutrition — written for real Indian runners in real Indian cities.</p>
<ul>
{items}
</ul>
</div></body></html>"""
    push("index.html", html, f"index: {len(entries)} posts · {datetime.now():%Y-%m-%d}")


def run():
    print(f"=== PACER Blog v3 — {POSTS_PER_RUN} posts — {datetime.now():%Y-%m-%d %H:%M} ===")
    if not GITHUB_TOKEN or not CLAUDE_KEY:
        print("ERROR: Missing secrets"); return

    existing = get_existing()
    print(f"Existing: {len(existing)}")

    # Priority: live trending → curated list
    live    = get_live_trending()
    curated = all_topics()
    queue   = []
    seen    = set()
    for t in live + curated:
        s = slug(t)
        if s not in existing and s not in seen:
            queue.append(t); seen.add(s)
        if len(queue) >= POSTS_PER_RUN: break

    print(f"Queue: {len(queue)} topics")
    new_entries = []

    for i, topic in enumerate(queue, 1):
        s = slug(topic)
        print(f"[{i}/{len(queue)}] {topic[:60]}")
        try:
            md   = write_post(topic)
            html = to_html(md, topic)
            title_m = re.search(r'<h1>(.+?)</h1>', html)
            title   = title_m.group(1) if title_m else topic.title()
            ok = push(f"{s}.html", html, f"blog: {topic[:55]}")
            if ok:
                new_entries.append((s, title))
                existing.add(s)
                print(f"  ✓ published")
            else:
                print(f"  ✗ push failed")
            time.sleep(2)
        except Exception as e:
            print(f"  ✗ {e}")

    if new_entries:
        all_e = [(s,t) for s,t in new_entries] + \
                [(s, s.replace('-',' ').title()) for s in existing
                 if s not in {e[0] for e in new_entries}]
        update_index(all_e)
        print(f"Index updated with {len(all_e)} total posts")

    if new_entries:
        update_published_log(new_entries)
        print(f"Published log updated: blog/published.json")

    print(f"\n=== Done. {len(new_entries)} new posts. Total: {len(existing)} ===")

if __name__ == "__main__":
    run()

# ── WIDGET INJECTION ─────────────────────────────────────────────
# Called from to_html() — inject live conditions widget into post body

WIDGET_SCRIPT = """
<div id="pacer-live-widget" data-city="{CITY}" style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0;font-family:'Inter',sans-serif;">
  <div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:16px">PACER · LIVE CONDITIONS · {CITY}</div>
  <div id="plw-loading" style="color:#555;font-size:14px">Checking conditions...</div>
  <div id="plw-content" style="display:none">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px">
      <div id="plw-time" style="font-size:12px;color:#555"></div>
      <div id="plw-badge" style="padding:7px 14px;border-radius:8px;font-size:12px;font-weight:800;letter-spacing:1px"></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:18px">
      <div style="background:rgba(255,255,255,.04);border-radius:10px;padding:12px;text-align:center">
        <div id="plw-aqi" style="font-size:22px;font-weight:800;color:#fff"></div>
        <div style="font-size:10px;color:#555;margin-top:2px;letter-spacing:1px">AQI</div>
      </div>
      <div style="background:rgba(255,255,255,.04);border-radius:10px;padding:12px;text-align:center">
        <div id="plw-hi" style="font-size:22px;font-weight:800;color:#fff"></div>
        <div style="font-size:10px;color:#555;margin-top:2px;letter-spacing:1px">HEAT INDEX</div>
      </div>
      <div style="background:rgba(255,255,255,.04);border-radius:10px;padding:12px;text-align:center">
        <div id="plw-hum" style="font-size:22px;font-weight:800;color:#fff"></div>
        <div style="font-size:10px;color:#555;margin-top:2px;letter-spacing:1px">HUMIDITY</div>
      </div>
    </div>
    <div id="plw-msg" style="font-size:13px;color:#777;line-height:1.6;margin-bottom:18px;padding:10px;background:rgba(255,255,255,.03);border-radius:8px"></div>
    <a href="https://usepacer.app" style="display:block;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">
      Get this every morning → usepacer.app
    </a>
  </div>
  <div id="plw-err" style="display:none;font-size:13px;color:#555">Check live conditions at <a href="https://usepacer.app" style="color:#4F9FFF">usepacer.app</a></div>
</div>
<script>
(function(){
  var city='{CITY}';
  var coords={Bangalore:{lat:12.97,lon:77.59},Mumbai:{lat:19.07,lon:72.87},Delhi:{lat:28.61,lon:77.20},Hyderabad:{lat:17.38,lon:78.48},Chennai:{lat:13.08,lon:80.27},Pune:{lat:18.52,lon:73.85},Kolkata:{lat:22.57,lon:88.36},Ahmedabad:{lat:23.02,lon:72.57},Jaipur:{lat:26.91,lon:75.78},Chandigarh:{lat:30.73,lon:76.77},Kochi:{lat:9.93,lon:76.26},Lucknow:{lat:26.84,lon:80.94},Nagpur:{lat:21.14,lon:79.08},Indore:{lat:22.71,lon:75.85},Coimbatore:{lat:11.01,lon:76.95},Bhubaneswar:{lat:20.29,lon:85.82}};
  var c=coords[city]||coords['Bangalore'];
  var K='b6907d289e10d714a6e88b30761fdd59';
  function hi(t,h){var F=t*9/5+32;return Math.round((-42.379+2.04901523*F+10.14333127*h-0.22475541*F*h-0.00683783*F*F-0.05481717*h*h+0.00122874*F*F*h+0.00085282*F*h*h-0.00000199*F*F*h*h-32)*5/9);}
  function vrd(a,hi){if(a>200||hi>44)return{t:'REST',bg:'#1a0a0a',c:'#ff4444'};if(a>150||hi>39)return{t:'WAIT',bg:'#1a1200',c:'#FF9500'};if(a>100||hi>34)return{t:'GO EASY',bg:'#101a0a',c:'#A3E635'};return{t:'GO',bg:'#0a1a0a',c:'#4ade80'};}
  function msg(v,a){var m={GO:'Good conditions. AQI safe, heat manageable. Good time to run.',WAIT:'Challenging conditions. AQI or heat is elevated. Keep it short and easy.','GO EASY':'Doable but tough. Run easy effort, shorten if needed.','REST':'Not recommended. AQI '+a+' or heat index too high. Rest or train indoors.'};return m[v]||'';}
  Promise.all([fetch('https://api.openweathermap.org/data/2.5/weather?lat='+c.lat+'&lon='+c.lon+'&units=metric&appid='+K),fetch('https://api.openweathermap.org/data/2.5/air_pollution?lat='+c.lat+'&lon='+c.lon+'&appid='+K)]).then(function(r){return Promise.all([r[0].json(),r[1].json()]);}).then(function(d){
    var t=Math.round(d[0].main.temp),h=Math.round(d[0].main.humidity),heat=hi(t,h),aqi=d[1].list[0].main.aqi*50,v=vrd(aqi,heat);
    document.getElementById('plw-time').textContent=new Date().toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'})+' IST';
    document.getElementById('plw-aqi').textContent=aqi;
    document.getElementById('plw-hi').textContent=heat+'°C';
    document.getElementById('plw-hum').textContent=h+'%';
    var b=document.getElementById('plw-badge');b.textContent=v.t;b.style.background=v.bg;b.style.color=v.c;b.style.border='1px solid '+v.c+'40';
    document.getElementById('plw-msg').textContent=msg(v.t,aqi);
    document.getElementById('plw-loading').style.display='none';
    document.getElementById('plw-content').style.display='block';
  }).catch(function(){document.getElementById('plw-loading').style.display='none';document.getElementById('plw-err').style.display='block';});
})();
</script>"""



# ════════════════════════════════════════════════════════════════════
# CONTEXTUAL CARDS — auto-detected from topic
# ════════════════════════════════════════════════════════════════════

def detect_card_type(topic):
    t = topic.lower()
    if any(k in t for k in ["food","eat","nutrition","diet","roti","sattu","banana",
                              "fuel","meal","carb","protein","nimbu","coconut","curd",
                              "idli","dosa","hydrat","electrolyte"]):
        return "food"
    if any(k in t for k in ["training","plan","5k","10k","marathon","coach","interval",
                              "pace","speed","cadence","tempo","fartlek","vo2","lactate",
                              "beginner","stamina","race","half marathon","full marathon",
                              "how to run","running plan","build","week"]):
        return "coaching"
    if any(k in t for k in ["where to run","running route","running park","place to run",
                              "best place","running track","running spot","running loop"]):
        return "places"
    # Default: conditions card (most universal)
    return "conditions"

def food_card():
    return """
<div style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">
  <div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:16px">PACER · PRE-RUN FUEL GUIDE</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px">
    <div style="background:rgba(255,255,255,.04);border-radius:10px;padding:14px;text-align:center">
      <div style="font-size:11px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">2 HRS BEFORE</div>
      <div style="font-size:13px;color:#fff;font-weight:600;line-height:1.6">Curd rice<br>Idli / Dosa<br>Dal + rice</div>
    </div>
    <div style="background:rgba(255,255,255,.04);border-radius:10px;padding:14px;text-align:center">
      <div style="font-size:11px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">30 MIN BEFORE</div>
      <div style="font-size:13px;color:#fff;font-weight:600;line-height:1.6">Banana<br>2–3 Dates<br>Sattu drink</div>
    </div>
    <div style="background:rgba(255,255,255,.04);border-radius:10px;padding:14px;text-align:center">
      <div style="font-size:11px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">AFTER RUN</div>
      <div style="font-size:13px;color:#fff;font-weight:600;line-height:1.6">Dal + rice<br>Curd + banana<br>Chaas</div>
    </div>
  </div>
  <div style="background:rgba(255,255,255,.03);border-radius:8px;padding:12px;margin-bottom:16px;font-size:13px;color:#666;line-height:1.6">
    <strong style="color:#aaa">Tip:</strong> In Indian heat, your body needs more electrolytes than in cooler conditions. PACER tells you what to expect before you step out — so you fuel for the actual conditions, not a training plan made for London.
  </div>
  <a href="https://usepacer.app" style="display:block;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">Check today's conditions → adjust your fuel plan</a>
</div>"""

def coaching_card():
    return """
<div style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">
  <div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:16px">PACER · SMART EFFORT GUIDE</div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:20px">
    <div style="background:rgba(74,222,128,.07);border:1px solid rgba(74,222,128,.2);border-radius:10px;padding:12px;text-align:center">
      <div style="font-size:15px;font-weight:900;color:#4ade80;margin-bottom:4px">GO</div>
      <div style="font-size:11px;color:#555">Full effort ok today</div>
    </div>
    <div style="background:rgba(163,230,53,.07);border:1px solid rgba(163,230,53,.2);border-radius:10px;padding:12px;text-align:center">
      <div style="font-size:11px;font-weight:900;color:#A3E635;margin-bottom:4px">GO EASY</div>
      <div style="font-size:11px;color:#555">Reduce intensity</div>
    </div>
    <div style="background:rgba(255,149,0,.07);border:1px solid rgba(255,149,0,.2);border-radius:10px;padding:12px;text-align:center">
      <div style="font-size:15px;font-weight:900;color:#FF9500;margin-bottom:4px">WAIT</div>
      <div style="font-size:11px;color:#555">Short run only</div>
    </div>
    <div style="background:rgba(255,68,68,.07);border:1px solid rgba(255,68,68,.2);border-radius:10px;padding:12px;text-align:center">
      <div style="font-size:15px;font-weight:900;color:#ff4444;margin-bottom:4px">REST</div>
      <div style="font-size:11px;color:#555">Skip. Train inside</div>
    </div>
  </div>
  <div style="background:rgba(255,255,255,.03);border-radius:8px;padding:12px;margin-bottom:16px;font-size:13px;color:#666;line-height:1.6">
    <strong style="color:#aaa">Every training plan assumes ideal conditions.</strong> In Indian heat, humidity, and monsoon, conditions change what effort is smart. PACER reads live AQI and heat and gives you one verdict before you head out.
  </div>
  <a href="https://usepacer.app" style="display:block;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">See today's training verdict for your city →</a>
</div>"""

def places_card(city="Bangalore"):
    SPOTS = {
        "Bangalore":[("Cubbon Park","12.9763,77.5929","5.8km loop · Shaded · Best before 7am"),
                     ("Lalbagh Botanical Garden","12.9507,77.5848","3km loop · Flat · Opens 6am"),
                     ("Nandi Hills","13.3702,77.6835","Trail runs · Cool climate · 1.5hrs from city"),
                     ("Ulsoor Lake","12.9815,77.6214","2km loop · Central · 5:30–7am window")],
        "Mumbai":[("Marine Drive","18.9322,72.8264","3.6km stretch · Sea breeze · Best before 7am"),
                  ("Carter Road Bandra","19.0728,72.8286","1km promenade · Popular 5:30–7am"),
                  ("Sanjay Gandhi NP","19.2147,72.9110","Trail running · Early morning · Security"),
                  ("Powai Lake","19.1196,72.9089","4km loop · IIT campus · 5:30–7am")],
        "Delhi":[("Lodhi Garden","28.5931,77.2197","2.1km loop · Historic · Opens 5am"),
                 ("Siri Fort","28.5491,77.2226","3km track · Well lit · Popular running group"),
                 ("Nehru Park Vasant Vihar","28.5963,77.1940","1.5km loop · Shaded · Safe"),
                 ("India Gate lawns","28.6129,77.2295","Road loop · Iconic · Early morning only")],
        "Hyderabad":[("KBR National Park","17.4156,78.4347","3km trail · Forest cover · Opens 5am"),
                     ("Hussain Sagar Lake","17.4239,78.4738","5km loop · Popular · Early morning best"),
                     ("Necklace Road","17.4126,78.4680","3km stretch · Lake views · 5:30–7am"),
                     ("Durgam Cheruvu","17.4344,78.3876","Trail loop · Rocky terrain · Peaceful")],
        "Chennai":[("Marina Beach","13.0500,80.2824","13km stretch · Flat · Best before 6:30am"),
                   ("Besant Nagar Beach","13.0002,80.2707","2km stretch · Less crowded · Good surface"),
                   ("Guindy National Park","13.0067,80.2206","Forest trail · Opens 8am · Cool shade"),
                   ("Adyar River walk","13.0067,80.2353","Riverside path · Quiet morning · Flat")],
        "Pune":[("Bund Garden","18.5359,73.8794","1.5km loop · Riverside · Good morning track"),
                ("Pune University campus","18.5590,73.8252","3km perimeter · Wide roads · 5–7am"),
                ("Vetal Hill","18.5368,73.8070","Trail · Panoramic views · Hilly circuit"),
                ("Pashan Lake","18.5424,73.7855","3km loop · Peaceful · Birding + running")],
        "Kolkata":[("Maidan","22.5502,88.3451","3km grass loop · Central · Best before 8am"),
                   ("Rabindra Sarobar","22.5142,88.3609","2km lake loop · Peaceful · 5–7am"),
                   ("Salt Lake","22.5764,88.4249","Wide roads · Grid layout · 5:30–7am"),
                   ("Victoria Memorial area","22.5448,88.3426","1.5km loop · Historic · Early morning")],
        "Ahmedabad":[("Sabarmati Riverfront","23.0225,72.5714","8km paved path · Flat · Shaded sections"),
                     ("Kankaria Lake","22.9821,72.5955","3km circular · Popular · Opens 6am"),
                     ("Law Garden area","23.0258,72.5618","1km loop · Night lit · Road running"),
                     ("ISKCON temple road","23.0447,72.5274","Quiet roads · Wide · Morning runners")],
    }
    spots = SPOTS.get(city, SPOTS["Bangalore"])
    items = ""
    for name, coords, desc in spots:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={coords}"
        items += f'''<div style="display:flex;align-items:flex-start;justify-content:space-between;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05);gap:12px">
      <div><div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:3px">{name}</div>
      <div style="font-size:12px;color:#555">{desc}</div></div>
      <a href="{maps_url}" target="_blank" rel="noopener" style="background:rgba(79,159,255,.1);border:1px solid rgba(79,159,255,.2);color:#4F9FFF;padding:6px 12px;border-radius:7px;font-size:11px;font-weight:600;text-decoration:none;white-space:nowrap;flex-shrink:0">Maps ↗</a>
    </div>'''
    return f'''
<div style="background:#0a0a0a;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;margin:36px 0">
  <div style="font-size:10px;font-weight:700;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:4px">PACER · TOP RUNNING SPOTS</div>
  <div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:16px">{city}</div>
  {items}
  <div style="margin-top:16px;background:rgba(255,255,255,.03);border-radius:8px;padding:12px;font-size:13px;color:#666;line-height:1.6">
    Check AQI and heat before heading to any of these spots. <strong style="color:#aaa">PACER</strong> gives you a GO/WAIT verdict every morning.
  </div>
  <a href="https://usepacer.app" style="display:block;margin-top:14px;background:#4F9FFF;color:#000;text-align:center;padding:12px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none">Check today's conditions in {city} →</a>
</div>'''

def get_card(topic):
    card_type = detect_card_type(topic)
    city = detect_city(topic)
    if card_type == "food":      return food_card()
    if card_type == "coaching":  return coaching_card()
    if card_type == "places":    return places_card(city)
    return ""  # conditions posts use the live widget instead


def detect_city(topic):
    """Pull city name from topic if it exists."""
    cities = ["Bangalore","Mumbai","Delhi","Hyderabad","Chennai","Pune","Kolkata",
              "Ahmedabad","Jaipur","Chandigarh","Kochi","Lucknow","Nagpur",
              "Indore","Coimbatore","Bhubaneswar","Surat","Vadodara"]
    for c in cities:
        if c.lower() in topic.lower():
            return c
    return "Bangalore"  # default for generic posts
