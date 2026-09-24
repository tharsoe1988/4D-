import streamlit as st
import requests
from datetime import datetime, timezone, timedelta

# Singapore Pools နောက်ခံအရောင်နှင့် စတိုင်လ်များ သတ်မှတ်ခြင်း
st.markdown(
    """
    <style>
    /* အဓိက App နောက်ခံအရောင်ကို Singapore Pools အပြာရောင်သို့ ပြောင်းရန် */
    .stApp {
        background-color: #1a4480;
        color: #ffffff;
    }
    
    /* စာသားများနှင့် ခေါင်းစဉ်များကို ပိုမိုထင်ရှားစေရန် */
    h1, h2, h3, p, label {
        color: #ffffff !important;
    }
    
    /* Input Box များကို ဒီဇိုင်းဆန်းသစ်ရန် */
    .stTextInput input {
        background-color: #ffffff;
        color: #000000;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Singapore 4D Engine", page_icon="🔢", layout="centered")

st.title("🇸🇬 Singapore 4D Smart-Query Engine")

# Singapore အချိန် (UTC+8) အရ လက်ရှိရက်စွဲကို ရယူခြင်း
sgt_time = datetime.now(timezone(timedelta(hours=8)))
current_date = sgt_time.strftime("%Y-%m-%d (%A)")
st.markdown(f"📅 **ရက်စွဲ:** {current_date}")

st.write("ထွက်ပြီးသားဆုများ စစ်ဆေးခြင်းနှင့် Candidate ရှာဖွေခြင်း (Online JSON)")

JSON_URL = "https://raw.githubusercontent.com/tharsoe1988/4D-/main/prizes.json"

@st.cache_data(ttl=60)
def load_prizes():
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("prizes", [])
    except Exception as e:
        st.error(f"Error loading prizes: {e}")
    return []

prizes_2026 = load_prizes()

original_grid = {
    "55": ["96", "99", "66"], "66": ["42", "44", "22"], "77": ["70", "77", "00"], 
    "88": ["53", "55", "33"], "99": ["81", "88", "11"],
    "56": ["94", "92", "64", "62"], "57": ["97", "90", "67", "60"],
    "58": ["95", "93", "65", "63"], "59": ["98", "91", "68", "61"],
    "67": ["47", "40", "27", "20"], "68": ["45", "43", "25", "23"],
    "69": ["48", "41", "28", "21"], "78": ["75", "73", "05", "03"],
    "79": ["78", "71", "08", "01"], "89": ["58", "51", "38", "31"]
}
group_order = ["55", "66", "77", "88", "99", "56", "57", "58", "59", "67", "68", "69", "78", "79", "89"]

@st.cache_data
def build_database(prizes_list):
    drawn_set = set(prizes_list)
    drawn_sorted_set = {"".join(sorted(p)) for p in prizes_list}
    exact_db, sorted_db, group_to_codes, code_to_group = {}, {}, {}, {}
    pairs_with_priority = {}
    for g in group_order:
        orig = original_grid[g]
        p_list = [{"p": p, "prio": 1, "is_rev": False} for p in orig]
        for p in orig:
            rev = p[::-1]
            if not any(x["p"] == rev for x in p_list): p_list.append({"p": rev, "prio": 2, "is_rev": True})
        pairs_with_priority[g] = p_list

    for prio_level in [1, 2]:
        for g1 in group_order:
            for g2 in group_order:
                for item1 in pairs_with_priority[g1]:
                    for item2 in pairs_with_priority[g2]:
                        if (1 if (item1["prio"] == 1 and item2["prio"] == 1) else 2) == prio_level:
                            code = item1["p"] + item2["p"]
                            sorted_code = "".join(sorted(code))
                            disp_g = f"{g1[::-1] if item1['is_rev'] else g1}-{g2[::-1] if item2['is_rev'] else g2}"
                            entry = {"group": disp_g, "code": code}
                            exact_db.setdefault(code, []).append(entry)
                            sorted_db.setdefault(sorted_code, []).append(entry)
                            group_to_codes.setdefault(disp_g, []).append(code)
                            code_to_group[code] = disp_g
    return exact_db, sorted_db, group_to_codes, code_to_group, drawn_set, drawn_sorted_set

exact_db, sorted_db, group_to_codes, code_to_group, drawn_set, drawn_sorted_set = build_database(prizes_2026)

user_input = st.text_input("Enter 4D digit(s) or Group (ဥပမာ - 6644):", "6644")

if user_input:
    for query in [q.strip() for q in user_input.replace(",", " ").split() if q.strip()]:
        st.markdown(f"--- Result for: **{query}** ---")
        if query in group_to_codes:
            st.success(f"📦 Group [{query}] Found:")
            for c in group_to_codes[query]:
                stat = " 🔴 **[EXACT DRAWN]**" if c in drawn_set else (" 🟠 **[PERM DRAWN]**" if "".join(sorted(c)) in drawn_sorted_set else "")
                st.write(f"- Code: `{c}`{stat}")
        elif len(query) == 4 and query.isdigit():
            found = False
            if query in exact_db:
                for item in exact_db[query]:
                    stat = " 🔴 **[EXACT DRAWN]**" if query in drawn_set else ""
                    st.success(f"✅ EXACT: `{item['code']}` ===> Group: **{item['group']}**{stat}")
                found = True
            sorted_val = "".join(sorted(query))
            if sorted_val in sorted_db:
                if found: st.info("--- Permutations ---")
                for item in sorted_db[sorted_val]:
                    if item['code'] != query:
                        p_stat = " 🟠 **[PERM DRAWN]**" if item['code'] in drawn_set or "".join(sorted(item['code'])) in drawn_sorted_set else ""
                        st.write(f"- Code: `{item['code']}` ===> Group: **{item['group']}**{p_stat}")
                        found = True
            if not found: st.error(f"❌ `{query}` ===> Not in Grid")
