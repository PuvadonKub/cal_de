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

# ==========================================
# ส่วนที่ 2: ตั้งค่าข้อมูลและฟอนต์
# ==========================================
try:
    fe = fm.FontEntry(fname="./Kanit-Regular.ttf", name='Kanit')
    fm.fontManager.ttflist.insert(0, fe)
    plt.rcParams['font.family'] = fe.name
except Exception:
    pass 

STATUS_OPTIONS = {
    "Pending": "⏳ รอจัดส่ง (Pending)",
    "In Transit": "🚚 กำลังขนส่ง (In Transit)",
    "Delivered": "✅ สำเร็จ (Delivered)"
}

PARCEL_TYPES = ["📦 พัสดุมาตรฐาน", "📄 เอกสารสำคัญ", "🍷 แตกหักง่าย", "🛋️ สินค้าชิ้นใหญ่"]

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

# --- ฟังก์ชัน Callback สำหรับกดปุ่มเปลี่ยนสถานะ (ทำงานก่อนหน้าจอโหลด) ---
def mark_as_delivered(tid):
    st.session_state.parcels_db[tid]["status"] = "Delivered"
    # บังคับอัปเดตค่าของ Dropdown ใน Tab 1 ให้ตรงกันล่วงหน้า
    st.session_state[f"status_{tid}"] = STATUS_OPTIONS["Delivered"]

# ==========================================
# ส่วนที่ 3: UI ของ Streamlit
# ==========================================
st.set_page_config(page_title="Smart Logistics", layout="wide", initial_sidebar_state="collapsed")
st.title("📦 Smart Logistics & Routing System")
st.markdown("ระบบจัดการคลังสินค้าและคำนวณเส้นทางจัดส่งอัจฉริยะ")

tab1, tab2, tab3 = st.tabs(["📋 จัดการรายการพัสดุ", "📍 คำนวณเส้นทาง (Routing)", "📊 แดชบอร์ดสรุปผล"])

# -----------------------------------------------------------------------------
# TAB 1: จัดการรายการพัสดุ
# -----------------------------------------------------------------------------
with tab1:
    with st.expander("➕ เพิ่มพัสดุใหม่เข้าสู่ระบบ", expanded=False):
        col1, col2, col3 = st.columns(3)
        co1, co2 = st.columns(2)
        with col1:
            new_tid = st.number_input("Tracking ID", min_value=1, step=1, key="new_tid")
            new_name = st.text_input("ชื่อผู้รับ", key="new_name")
        with col2:
            new_type = st.selectbox("ประเภทพัสดุ", PARCEL_TYPES)
        with col3:
            new_origin = st.selectbox("ต้นทาง", list(G.nodes()), key="new_org")
            new_dest = st.selectbox("ปลายทาง", list(G.nodes()), key="new_dest")
        with co1:
            if st.button("💾 บันทึกพัสดุ", use_container_width=True, type="primary"):
                if new_tid not in st.session_state.parcels_db and new_name:
                    try:
                        dist = nx.dijkstra_path_length(G, new_origin, new_dest, weight='weight')
                        cost = BASE_FARE + (dist * RATE_PER_KM)
                        st.session_state.parcels_db[new_tid] = {
                            "name": new_name, "type": new_type, "origin": new_origin, "dest": new_dest,
                            "status": "Pending", "dist": dist, "cost": cost
                        }
                        st.session_state.tracking_list.append(new_tid)
                        st.session_state.name_list.append(new_name)
                        st.success(f"เพิ่มรหัส {new_tid} สำเร็จ!")
                    except Exception:
                        st.error("ไม่มีเส้นทางเชื่อมต่อกัน")
                else:
                    st.error("ข้อมูลไม่ครบถ้วนหรือรหัสซ้ำ!")


    st.divider()

    st.subheader("🔍 ค้นหาและจัดการพัสดุ")
    f_col1, f_col2 = st.columns([1, 1])
    search_query = f_col1.text_input("ค้นหา (ระบุชื่อผู้รับหรือ Tracking ID)")
    filter_types = f_col2.multiselect("🏷️ กรองตามประเภทพัสดุ", PARCEL_TYPES, default=PARCEL_TYPES)

    sorted_tracking = st.session_state.tracking_list.copy()
    if len(sorted_tracking) > 0:
        if len(sorted_tracking) < 43:
            sorted_tracking = insertionSort(sorted_tracking)
            st.caption("ℹ️ แสดงผลโดยจัดเรียงรหัสด้วย *Insertion Sort*")
        else:
            sorted_tracking = mergeSort(sorted_tracking)
            st.caption("ℹ️ แสดงผลโดยจัดเรียงรหัสด้วย *Merge Sort*")

    display_list = sorted_tracking
    if search_query:
        if search_query.isdigit():
            target_id = int(search_query)
            idx = binarySearch(sorted_tracking, 0, len(sorted_tracking) - 1, target_id)
            display_list = [sorted_tracking[idx]] if idx != -1 else []
        else:
            indices = fuzzyLinearSearch(st.session_state.name_list, search_query)
            display_list = [st.session_state.tracking_list[i] for i in indices]

    st.markdown("---")
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6, h_col7 = st.columns([0.8, 1.2, 1.2, 1.8, 1.5, 1, 0.8])
    h_col1.write("**ID**")
    h_col2.write("**ชื่อผู้รับ**")
    h_col3.write("**ประเภท**")
    h_col4.write("**เส้นทาง**")
    h_col5.write("**สถานะ**")
    h_col6.write("**ราคา**")
    h_col7.write("**จัดการ**")

    count_displayed = 0
    for tid in display_list:
        data = st.session_state.parcels_db.get(tid)
        if not data: continue
        
        p_type = data.get("type", "📦 พัสดุมาตรฐาน")
        if p_type not in filter_types: continue 

        count_displayed += 1
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6, r_col7 = st.columns([0.8, 1.2, 1.2, 1.8, 1.5, 1, 0.8])
        r_col1.write(f"`{tid}`")
        r_col2.write(data["name"])
        r_col3.write(p_type)
        r_col4.write(f"{data['origin']} ➔ {data['dest']}")

        current_status_val = data["status"]
        status_list = list(STATUS_OPTIONS.keys())
        status_labels = list(STATUS_OPTIONS.values())

        new_status_label = r_col5.selectbox(
            "", status_labels, index=status_list.index(current_status_val),
            key=f"status_{tid}", label_visibility="collapsed"
        )
        new_status_key = [k for k, v in STATUS_OPTIONS.items() if v == new_status_label][0]

        if new_status_key != current_status_val:
            st.session_state.parcels_db[tid]["status"] = new_status_key
            st.rerun()

        r_col6.write(f"฿{data['cost']}")

        if r_col7.button("🗑️", key=f"del_{tid}", help="ลบพัสดุ"):
            name_to_rem = data["name"]
            del st.session_state.parcels_db[tid]
            st.session_state.tracking_list.remove(tid)
            st.session_state.name_list.remove(name_to_rem)
            st.rerun()
            
    if count_displayed == 0:
        st.info("ไม่พบรายการพัสดุที่ตรงกับเงื่อนไข")

# -----------------------------------------------------------------------------
# TAB 2: คำนวณเส้นทางและอุปสรรค
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("🗺️ จำลองเส้นทางและคำนวณการจัดส่ง")

    in_transit_list = {tid: d for tid, d in st.session_state.parcels_db.items() if d["status"] == "In Transit"}

    if not in_transit_list:
        st.warning("⚠️ ไม่มีพัสดุสถานะ 'In Transit' กรุณาเปลี่ยนสถานะพัสดุในหน้าแรกก่อน")
    else:
        parcel_options = [f"{tid} - {d['name']} ({d['origin']} ➔ {d['dest']})" for tid, d in in_transit_list.items()]
        col_sel, col_btn = st.columns([3, 1])
        selected_option = col_sel.selectbox("พัสดุที่กำลังจัดส่ง:", options=parcel_options, label_visibility="collapsed")
        
        selected_tid = int(selected_option.split(" - ")[0])
        parcel_data = in_transit_list[selected_tid]

        # ✅ แก้ไขตรงนี้: ใช้ on_click เพื่อรันฟังก์ชันอัปเดตก่อนการโหลดหน้าจอ
        col_btn.button(
            "✅ ขนส่งสำเร็จ", 
            key=f"btn_success_{selected_tid}", 
            type="primary", 
            use_container_width=True,
            on_click=mark_as_delivered, # เรียกใช้ Callback ทันทีเมื่อปุ่มถูกกด
            args=(selected_tid,)      # ส่งรหัสไปให้ฟังก์ชัน
        )

        st.markdown("##### 🚧 จำลองอุปสรรคบนท้องถนน")
        all_edges = [f"{u} - {v}" for u, v in G.edges()]
        closed_roads = st.multiselect(
            "เลือกเส้นทางที่ 'ถนนปิด' หรือ 'รถติดหนัก' (ระบบจะหาทางเลี่ยงอัตโนมัติ):", options=all_edges
        )

        if st.button(f"🚀 คำนวณเส้นทางใหม่", use_container_width=True):
            try:
                s_node, e_node = parcel_data["origin"], parcel_data["dest"]
                G_temp = G.copy()
                for road in closed_roads:
                    u, v = road.split(" - ")
                    if G_temp.has_edge(u, v): G_temp.remove_edge(u, v)

                path = nx.dijkstra_path(G_temp, source=s_node, target=e_node, weight='weight')
                dist = nx.dijkstra_path_length(G_temp, source=s_node, target=e_node, weight='weight')

                st.success(f"📦 พัสดุรหัส {selected_tid} | ผู้รับ: {parcel_data['name']} | 🚩 เส้นทาง: {' ➔ '.join(path)}")

                # --- การวาดกราฟ Kamada-Kawai ---

                # [Image of Dijkstra's algorithm]

                fig, ax = plt.subplots(figsize=(12, 8))

                # จัดการฟอนต์
                font_name = "sans-serif"
                try:
                    font_path = "./Kanit-Regular.ttf"
                    fe = fm.FontEntry(fname=font_path, name='Kanit')
                    fm.fontManager.ttflist.insert(0, fe)
                    plt.rcParams['font.family'] = fe.name
                    font_name = fe.name
                except: pass

                # 1. กำหนดกลุ่มจังหวัดวงใน (ศูนย์กลาง)
                inner_shell = ["ปทุมธานี", "กรุงเทพ","นนทบุรี"]

                # ใส่ชื่อจังหวัดเรียงตามลำดับที่คุณอยากให้อยู่บนวงกลม (ตามเข็มนาฬิกา)
                outer_shell = ["สมุทรปราการ", "สมุทรสาคร", "นครปฐม", "สระบุรี", "พระนครศรีอยุธยา", "นครนายก"]

                # 3. วาดกราฟแบบ Shell
                pos = nx.shell_layout(G, nlist=[inner_shell, outer_shell], scale=3)

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

# -----------------------------------------------------------------------------
# TAB 3: แดชบอร์ดสรุปผล 
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📊 ภาพรวมคลังสินค้าและการจัดส่ง")
    
    all_p = list(st.session_state.parcels_db.values())
    total_parcels = len(all_p)
    
    if total_parcels == 0:
        st.info("ยังไม่มีข้อมูลพัสดุในระบบสำหรับวิเคราะห์")
    else:
        df = pd.DataFrame(all_p)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📦 พัสดุทั้งหมด", f"{total_parcels} ชิ้น")
        m2.metric("✅ ส่งสำเร็จ", f"{len(df[df['status'] == 'Delivered'])} ชิ้น")
        m3.metric("🚚 กำลังจัดส่ง", f"{len(df[df['status'] == 'In Transit'])} ชิ้น")
        m4.metric("💸 รายได้ทั้งหมด (บาท)", f"฿{df['cost'].sum():,.2f}")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**พัสดุที่ส่งสำเร็จแยกตามประเภท**")
            delivered_df = df[df['status'] == 'Delivered']
            if not delivered_df.empty:
                type_counts = delivered_df['type'].value_counts()
                
                fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
                ax_bar.bar(type_counts.index, type_counts.values, color="#4facfe")
                ax_bar.set_ylabel("จำนวน (ชิ้น)", fontsize=10)
                plt.xticks(rotation=15, fontsize=10)
                st.pyplot(fig_bar)
            else:
                st.write("ยังไม่มีพัสดุที่ส่งสำเร็จ")
                
        with c2:
            st.markdown("**สัดส่วนสถานะพัสดุทั้งหมด**")
            status_counts = df['status'].value_counts()
            
            fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
            
            thai_labels = [STATUS_OPTIONS.get(k, k).split(" ")[1] for k in status_counts.index]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            
            ax_pie.pie(status_counts.values, labels=thai_labels, autopct='%1.1f%%', 
                       startangle=90, colors=colors[:len(status_counts)], textprops={'fontsize': 10})
            ax_pie.axis('equal')  
            st.pyplot(fig_pie)
            
        st.caption("แดชบอร์ดอัปเดตข้อมูลแบบ Real-time ตามสถานะจริงในระบบ")
