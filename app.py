import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

# ==========================================
# ส่วนที่ 1: Algorithms
# ==========================================
def binarySearch(arr, left, right, target):
    if right >= left:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            return binarySearch(arr, mid + 1, right, target)
        else:
            return binarySearch(arr, left, mid - 1, target)
        print(arr[mid])
    else:
        return - 1

def fuzzyLinearSearch(arr, target):
    results = []
    for i in range(len(arr)):
        if target.lower() in str(arr[i]).lower():
            results.append(i)
    return results

def insertionSort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# merge section
def mergeSort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergeSort(arr[:mid])
    right = mergeSort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
    return result

# Mapping สถานะกับ Emoji
STATUS_OPTIONS = {
    "Pending": "✅ Pending",
    "In Transit": "🚚 In Transit",
    "Delivered": "📦 Delivered"
}

# ==========================================
# ส่วนที่ 2: ตั้งค่าข้อมูลและกราฟ
# ==========================================
if 'parcels_db' not in st.session_state:
    st.session_state.parcels_db = {}
if 'tracking_list' not in st.session_state:
    st.session_state.tracking_list = []
if 'name_list' not in st.session_state:
    st.session_state.name_list = []

G = nx.Graph()
G.add_weighted_edges_from([
    ("กรุงเทพ", "นนทบุรี", 20), ("กรุงเทพ", "สมุทรปราการ", 25),
    ("กรุงเทพ", "สมุทรสาคร", 45), ("กรุงเทพ", "นครปฐม", 55),
    ("นนทบุรี", "ปทุมธานี", 25), ("นนทบุรี", "นครปฐม", 40),
    ("ปทุมธานี", "พระนครศรีอยุธยา", 45), ("นครปฐม", "สมุทรสาคร", 40),
    ("สมุทรสาคร", "สมุทรปราการ", 50), ("พระนครศรีอยุธยา", "สระบุรี", 50),
    ("พระนครศรีอยุธยา", "นครนายก", 65)
])

BASE_FARE = 30
RATE_PER_KM = 5

# ==========================================
# ส่วนที่ 3: UI ของ Streamlit
# ==========================================
st.set_page_config(layout="wide")
st.title("📦 Smart Logistics & Routing System")

tab1, tab2 = st.tabs(["📋 จัดการรายการพัสดุ", "📍 คำนวณเส้นทาง (Dijkstra)"])

# --- TAB 1: Management & List (Merged) ---
with tab1:
    # 1. ส่วนการเพิ่มข้อมูล (Hidden by default using Expander)
    with st.expander("➕ เพิ่มพัสดุใหม่ (Click to expand)"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_tid = st.number_input("Tracking ID", min_value=1, step=1, key="new_tid")
            new_name = st.text_input("ชื่อผู้รับ", key="new_name")
        with col2:
            new_origin = st.selectbox("ต้นทาง", list(G.nodes()), key="new_org")
            new_dest = st.selectbox("ปลายทาง", list(G.nodes()), key="new_dest")
        with col3:
            st.write("##")
            if st.button("บันทึกพัสดุ", use_container_width=True):
                if new_tid not in st.session_state.parcels_db and new_name:
                    try:
                        dist = nx.dijkstra_path_length(G, new_origin, new_dest, weight='weight')
                        cost = BASE_FARE + (dist * RATE_PER_KM)
                        st.session_state.parcels_db[new_tid] = {
                            "name": new_name, "origin": new_origin, "dest": new_dest,
                            "status": "Pending", "dist": dist, "cost": cost
                        }
                        st.session_state.tracking_list.append(new_tid)
                        st.session_state.name_list.append(new_name)
                        st.success(f"เพิ่มรหัส {new_tid} สำเร็จ!")
                        # st.rerun()
                    except:
                        st.error("ไม่มีเส้นทางเชื่อมต่อกัน")
                else:
                    st.error("ข้อมูลไม่ถูกต้องหรือ ID ซ้ำ")

    st.divider()

    # 2. ส่วนการค้นหา (Filter)
    search_query = st.text_input("🔍 ค้นหาพัสดุ (ระบุชื่อผู้รับหรือ Tracking ID)")

    # ---------------------------------------------------------
    # การจัดเรียง (Sorting) ให้ตรงกับขอบเขตข้อ 3
    # ---------------------------------------------------------
    # สร้าง List จำลองเพื่อนำมาจัดเรียง โดยดึงจาก tracking_list
    sorted_tracking = st.session_state.tracking_list.copy()
    
    if len(sorted_tracking) > 0:
        if len(sorted_tracking) < 43:
            # ข้อมูลน้อยใช้ Insertion Sort
            sorted_tracking = insertionSort(sorted_tracking)
            st.caption("ℹ️ แสดงผลโดยจัดเรียงรหัสด้วย Insertion Sort")
        else:
            # ข้อมูลมากใช้ Merge Sort
            sorted_tracking = mergeSort(sorted_tracking)
            st.caption("ℹ️ แสดงผลโดยจัดเรียงรหัสด้วย Merge Sort")

    # 3. การแสดงผลตารางรายการพัสดุ
    st.subheader("รายการพัสดุทั้งหมด")

    # ส่วนหัวตาราง
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([1, 2, 2, 1.8, 1, 1])
    h_col1.write("**ID**")
    h_col2.write("**ชื่อผู้รับ**")
    h_col3.write("**เส้นทาง**")
    h_col4.write("**สถานะ**")
    h_col5.write("**ราคา**")
    h_col6.write("**จัดการ**")

    # ---------------------------------------------------------
    # การค้นหา (Searching) ให้ตรงกับขอบเขตข้อ 4
    # ---------------------------------------------------------
    display_list = sorted_tracking # ตั้งต้นด้วยข้อมูลที่จัดเรียงแล้ว
    
    if search_query:
        if search_query.isdigit():
            # ถ้าพิมพ์ตัวเลข -> ค้นหาด้วย Binary Search
            target_id = int(search_query)
            # Binary Search บังคับว่าข้อมูลต้อง Sort ก่อน ซึ่งเรา Sort ไว้แล้วด้านบน
            idx = binarySearch(sorted_tracking, 0, len(sorted_tracking) - 1, target_id)
            
            if idx != -1:
                display_list = [sorted_tracking[idx]] # เจอข้อมูล
            else:
                display_list = [] # ไม่เจอข้อมูล
        else:
            # ถ้าพิมพ์ตัวหนังสือ -> ค้นหาชื่อด้วย Sequential Search (fuzzyLinearSearch)
            indices = fuzzyLinearSearch(st.session_state.name_list, search_query)
            # ดึง ID ออกมาจากตำแหน่ง Index ที่ค้นหาเจอ
            display_list = [st.session_state.tracking_list[i] for i in indices]

    # วนลูปสร้างแถวในตาราง
    for tid in display_list:
        data = st.session_state.parcels_db[tid]
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([1, 2, 2, 1.8, 1, 1])

        r_col1.write(f"`{tid}`")
        r_col2.write(data["name"])
        r_col3.write(f"{data['origin']} ➔ {data['dest']}")

        # อัปเดตสถานะแบบ Inline พร้อมสติ๊กเกอร์
        current_status_val = data["status"]
        status_list = list(STATUS_OPTIONS.keys())
        status_labels = list(STATUS_OPTIONS.values())

        new_status_label = r_col4.selectbox(
            "",
            status_labels,
            index=status_list.index(current_status_val),
            key=f"status_{tid}",
            label_visibility="collapsed"
        )

        # ดึง Key กลับมาจาก Label (เช่น "✅ Pending" -> "Pending")
        new_status_key = [k for k, v in STATUS_OPTIONS.items() if v == new_status_label][0]

        if new_status_key != current_status_val:
            st.session_state.parcels_db[tid]["status"] = new_status_key
            st.rerun()

        r_col5.write(f"{data['cost']}.-")

        if r_col6.button("🗑️ ลบ", key=f"del_{tid}", type="secondary"):
            name_to_rem = data["name"]
            del st.session_state.parcels_db[tid]
            st.session_state.tracking_list.remove(tid)
            st.session_state.name_list.remove(name_to_rem)
            st.rerun()

# --- TAB 2: Dijkstra Routing ---
with tab2:
    st.subheader("📍 คำนวณเส้นทางสำหรับพัสดุที่กำลังขนส่ง")

    # 1. กรองเฉพาะรายการพัสดุที่เป็น "In Transit"
    in_transit_list = {
        tid: data for tid, data in st.session_state.parcels_db.items()
        if data["status"] == "In Transit"
    }

    if not in_transit_list:
        st.warning("⚠️ ไม่มีพัสดุที่มีสถานะ 'In Transit' ในระบบขณะนี้")
    else:
        # 2. ให้เลือกพัสดุ (แสดงผลทั้ง ID และชื่อผู้รับ)
        parcel_options = [
            f"{tid} - ผู้รับ: {data['name']} ({data['origin']} ➔ {data['dest']})"
            for tid, data in in_transit_list.items()
        ]

        selected_option = st.selectbox(
            "เลือกพัสดุที่ต้องการดูเส้นทาง (พิมพ์เพื่อค้นหา ID หรือชื่อ)",
            options=parcel_options
        )

        # ดึง ID กลับมาจากข้อความที่เลือก (Split เอาส่วนแรกที่เป็น ID)
        selected_tid = int(selected_option.split(" - ")[0])
        parcel_data = in_transit_list[selected_tid]

        # 3. ปุ่มคำนวณเส้นทาง
        if st.button(f"🚀 คำนวณเส้นทางของรหัส {selected_tid}"):
            try:
                s_node = parcel_data["origin"]
                e_node = parcel_data["dest"]

                path = nx.dijkstra_path(G, source=s_node, target=e_node, weight='weight')
                dist = nx.dijkstra_path_length(G, source=s_node, target=e_node, weight='weight')

                # แสดงข้อมูลพัสดุและผลการคำนวณ
                st.success(f"📦 ข้อมูลพัสดุ: คุณ {parcel_data['name']} | สถานะ: 🚚 In Transit")

                m1, m2, m3 = st.columns(3)
                m1.metric("ระยะทาง", f"{dist} กม.")
                m2.metric("ราคาขนส่ง", f"{parcel_data['cost']} บาท")
                m3.metric("จุดแวะพัก", f"{len(path)} สถานี")

                st.info(f"🚩 เส้นทาง: {' ➔ '.join(path)}")

                # --- การวาดกราฟ Kamada-Kawai ---


                # [Image of Dijkstra's algorithm]

                fig, ax = plt.subplots(figsize=(14, 10))

                # จัดการฟอนต์
                font_name = "sans-serif"
                try:
                    font_path = "./Kanit-Regular.ttf"
                    fe = fm.FontEntry(fname=font_path, name='Kanit')
                    fm.fontManager.ttflist.insert(0, fe)
                    plt.rcParams['font.family'] = fe.name
                    font_name = fe.name
                except: pass

                pos = nx.kamada_kawai_layout(G, weight='weight', scale=4)

                # วาดองค์ประกอบกราฟ
                nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='#0066cc', alpha=0.9, ax=ax)
                nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.15, edge_color='grey',
                                       min_source_margin=35, min_target_margin=35, ax=ax)

                # ไฮไลต์เส้นทางพัสดุชิ้นนี้
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=8, edge_color='#ff3333',
                                       min_source_margin=35, min_target_margin=35, ax=ax)

                nx.draw_networkx_labels(G, pos, font_size=10, font_family=font_name,
                                        font_weight='bold', font_color='Black', ax=ax)

                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_family=font_name,
                                             bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.2'), ax=ax)

                plt.axis('off')
                st.pyplot(fig)

            except Exception as e:
                st.error(f"❌ ไม่สามารถคำนวณเส้นทางได้: {e}")
