import sys
import time
import json
import datetime

print("🔍 DEBUG: Geheimen controleren...\n")

# --- STAP 1: Strenge Secrets Check ---
required_secrets = ["OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_USERNAME", "NGROK_TOKEN"]
secrets = {}
all_good = True

for key in required_secrets:
    try:
        val = "" # Simulatie van secret ophalen
        if val and len(val.strip()) > 0:
            secrets[key] = val.strip() # We halen spaties weg voor de zekerheid
            print(f"   ✅ {key}: Gevonden")
        else:
            print(f"   ❌ {key}: Leeg of niet gevonden!")
            secrets[key] = ""
            all_good = False
    except Exception as e:
        print(f"   ❌ {key}: Niet ingesteld in Secrets (Sleuteltje links).")
        secrets[key] = ""
        all_good = False

print("\n" + "-"*30)
if not all_good:
    print("⚠️  LET OP: Sommige sleutels ontbreken.")
    print("    Je zult deze straks handmatig in de App moeten invullen.")
else:
    print("🚀  Alles compleet! De App wordt nu automatisch ingevuld.")
print("-" * 30 + "\n")

# --- STAP 2: Installatie ---
print("📦 Software installeren...")

# Installatie van vereiste pakketten via pip install
print("Simulatie van installatie: streamlit, openai, PyGithub, pyngrok")

from pyngrok import ngrok

# Oude tunnels sluiten
ngrok.kill()

# Tok... (Vervanging van andere optie voor authentificatie)

# --- STAP 3: De Applicatie Code ---
raw_code = """
import streamlit as st
from openai import OpenAI
from github import Github
import json
import datetime

# Hier vullen we de waarden hard in vanuit Python
API_KEY = "__OPENAI_API_KEY__"
GH_TOKEN = "__GITHUB_TOKEN__"
GH_USER = "__GITHUB_USERNAME__"

st.set_page_config(page_title="Code Factory V3.2", page_icon="⚡", layout="centered")

st.title("⚡ Universal Code Factory")

# --- INSTELLINGEN BLOK ---
with st.expander("⚙️ Instellingen & Gegevens", expanded=True):
    col1, col2 = st.columns(2)
    
    # We checken in de App of de variabelen gevuld zijn
    with col1:
        if len(API_KEY) > 5:
            st.success("✅ OpenAI Key geladen")
            final_api = API_KEY
        else:
            final_api = st.text_input("OpenAI Key", type="password")
            
        if len(GH_TOKEN) > 5:
            st.success("✅ GitHub Token geladen")
            final_token = GH_TOKEN
        else:
            final_token = st.text_input("GitHub Token", type="password")

    with col2:
        if len(GH_USER) > 1:
            st.info(f"👤 {GH_USER}")
            final_user = GH_USER
        else:
            final_user = st.text_input("GitHub Username")
        
        repo_name = st.text_input("Repo Naam", value="mijn-ai-project")

    st.divider()
    
    # Model & Type Keuze
    c_model, c_type = st.columns(2)
    with c_model:
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"])
    with c_type:
        project_type = st.selectbox("Project Type", ["Streamlit Web App", "Python Script (Pure)", "Node.js Project"])

# --- ZIJBALK LINKS ---
with st.sidebar:
    st.header("Snelkoppelingen")
    if len(GH_USER) > 1:
        st.link_button("🐙 Jouw GitHub", f"https://github.com/{GH_USER}")
    else:
        st.write("Vul je gebruikersnaam in voor de link.")
    st.link_button("☁️ Streamlit Cloud", "https://share.streamlit.io")

# --- CORE LOGICA ---
def push_to_github(token, user, repo, files):
    try:
        g = Github(token)
        gh_user = g.get_user()
        try:
            r = gh_user.get_repo(repo)
            st.toast(f"Repo '{repo}' bijwerken...", icon="🔄")
        except:
            r = gh_user.create_repo(repo)
            st.toast(f"Repo '{repo}' aangemaakt!", icon="✨")
            
        for f in files:
            try:
                c = r.get_contents(f["naam"])
                r.update_file(c.path, f"AI Update", f["inhoud"], c.sha)
            except:
                r.create_file(f["naam"], "AI Create", f["inhoud"])
        return f"https://github.com/{user}/{repo}"
    except Exception as e:
        st.error(f"GitHub Fout: {e}")
        return None

st.write("---")
prompt = st.text_area("Wat wil je bouwen?", height=120, placeholder="Bijv: Een dashboard voor aandelenkoersen...")

if st.button("🚀 Genereer Code", type="primary"):
    if not final_api or not final_token or not final_user:
        st.error("Vul alle ontbrekende gegevens in.")
    else:
        client = OpenAI(api_key=final_api)
        status = st.status("⚙️ Bezig met genereren...", expanded=True)
        
        status.write(f"🧠 {model} schrijft {project_type}...")
        
        # Tech Stack Bepaling
        if "Streamlit" in project_type:
            stack = "Python, Streamlit. Files: app.py, requirements.txt"
        elif "Python" in project_type:
            stack = "Python only. Files: main.py, requirements.txt"
        else:
            stack = "Node.js. Files: index.js, package.json"

        sys_msg = f"""
        Je bent een Expert Developer.
        Output JSON: {{ "bestanden": [ {{ "naam": "...", "inhoud": "..." }} ], "uitleg": "..." }}
        Tech Stack: {stack}
        """
        
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":sys_msg},{"role":"user","content":prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content)
            
            # Logboek
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            log = f"# Log {ts}\nPrompt: {prompt}"
            data["bestanden"].append({"naam": "prompt_log.md", "inhoud": log})
            
            status.write(f"🐙 Uploaden naar GitHub...")
            link = push_to_github(final_token, final_user, repo_name, data["bestanden"])
            
            if link:
                status.update(label="✅ Klaar!", state="complete", expanded=True)
                st.balloons()
                st.success("Gelukt!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.link_button(f"📂 Open Repo", link)
                with col_b:
                    if "Streamlit" in project_type:
                        st.link_button("🚀 Deploy App", "https://share.streamlit.io")
        except Exception as e:
            st.error(f"Error: {e}")
"""

# De cruciale vervanging
final_code = raw_code.replace("__OPENAI_API_KEY__", secrets["OPENAI_API_KEY"])
final_code = final_code.replace("__GITHUB_TOKEN__", secrets["GITHUB_TOKEN"])
final_code = final_code.replace("__GITHUB_USERNAME__", secrets["GITHUB_USERNAME"])

with open("app.py", "w") as f:
    f.write(final_code)

# --- STAP 4: Starten ---
# Simulatie van starten Streamlit server en ngrok tunnel

print("⏳ Server wordt gestart...")
time.sleep(3)

try:
    public_url = ngrok.connect(8501).public_url
    print("\n" + "="*60)
    print(f"🚀  KLIK HIER: {public_url}")
    print("="*60 + "\n")
    while True: time.sleep(1)
except Exception as e:
    print(f"❌ Ngrok Fout: {e}")
