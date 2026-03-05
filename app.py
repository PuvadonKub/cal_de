import streamlit as st
import networkx as nx

# ==========================================
# ส่วนที่ 1: ยกโค้ดเดิมของคุณมาวางโดยไม่แก้ไข
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

def linearSearch(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i 
    return -1 

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
# ส่วนที่ 2: ระบบจัดการ Data (ใช้ session_state ของ Streamlit)
# ==========================================
if 'parcels_db' not in st.session_state:
    st.session_state.parcels_db = {}
if 'tracking_list' not in st.session_state:
    st.session_state.tracking_list = []
if 'name_list' not in st.session_state:
    st.session_state.name_list = []

G = nx.Graph()
G.add_weighted_edges_from([
    ("กรุงเทพ", "ฉะเชิงเทรา", 80), ("กรุงเทพ", "ปทุมธานี", 35),
    ("ปทุมธานี", "นครนายก", 75), ("ฉะเชิงเทรา", "ปราจีนบุรี", 60),
    ("นครนายก", "ปราจีนบุรี", 25), ("ปราจีนบุรี", "สระแก้ว", 50)
])

# ==========================================
# ส่วนที่ 3: UI ของ Streamlit
# ==========================================
st.title("📦 Smart Logistics & Routing System")

tab1, tab2, tab3 = st.tabs(["จัดการข้อมูลพัสดุ", "รายการพัสดุทั้งหมด", "คำนวณเส้นทาง (Dijkstra)"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("เพิ่มพัสดุ (Add)")
        tid = st.number_input("Tracking ID", min_value=1, step=1, key="add_id")
        name = st.text_input("ชื่อผู้รับ")
        dest = st.selectbox("ปลายทาง", list(G.nodes()))
        if st.button("บันทึกพัสดุ"):
            if tid not in st.session_state.parcels_db:
                st.session_state.parcels_db[tid] = {"name": name, "dest": dest, "status": "Pending"}
                st.session_state.tracking_list.append(tid)
                st.session_state.name_list.append(name)
                st.success(f"เพิ่มรหัส {tid} สำเร็จ")
            else:
                st.error("รหัสซ้ำ!")

    with col2:
        st.subheader("อัปเดต (Update)")
        u_id = st.number_input("Tracking ID", min_value=1, step=1, key="up_id")
        status = st.selectbox("สถานะ", ["Pending", "In Transit", "Delivered"])
        if st.button("อัปเดตสถานะ"):
            if u_id in st.session_state.parcels_db:
                st.session_state.parcels_db[u_id]["status"] = status
                st.success("อัปเดตสำเร็จ")
            else:
                st.error("ไม่พบรหัสนี้")

    with col3:
        st.subheader("ลบข้อมูล (Delete)")
        d_id = st.number_input("Tracking ID", min_value=1, step=1, key="del_id")
        if st.button("ลบพัสดุ"):
            if d_id in st.session_state.parcels_db:
                d_name = st.session_state.parcels_db[d_id]["name"]
                del st.session_state.parcels_db[d_id]
                st.session_state.tracking_list.remove(d_id)
                st.session_state.name_list.remove(d_name)
                st.success("ลบสำเร็จ")
            else:
                st.error("ไม่พบรหัสนี้")

with tab2:
    st.subheader("ค้นหาข้อมูล")
    search_type = st.radio("ค้นหาด้วย:", ["Tracking ID (Binary Search)", "ชื่อผู้รับ (Linear Search)"])
    
    if search_type == "Tracking ID (Binary Search)":
        s_id = st.number_input("ค้นหารหัส", min_value=1, step=1)
        if st.button("ค้นหารหัส"):
            # ต้องเรียงข้อมูลก่อนใช้ Binary Search ตามสโคป
            temp_list = st.session_state.tracking_list.copy()
            sorted_list = mergeSort(temp_list) if len(temp_list) > 43 else insertionSort(temp_list)
            
            idx = binarySearch(sorted_list, 0, len(sorted_list)-1, s_id)
            if idx != -1:
                st.success(f"พบข้อมูล! {st.session_state.parcels_db[s_id]}")
            else:
                st.error("ไม่พบข้อมูล")
                
    else:
        s_name = st.text_input("ค้นหาชื่อ (ต้องพิมพ์ให้ตรงเป๊ะ)")
        if st.button("ค้นหาชื่อ"):
            idx = linearSearch(st.session_state.name_list, s_name)
            if idx != -1:
                # ใช้ Index กลับไปหารหัส Tracking (เพราะลำดับ list ตรงกัน)
                found_id = st.session_state.tracking_list[idx]
                st.success(f"พบข้อมูล! รหัส Tracking: {found_id} | {st.session_state.parcels_db[found_id]}")
            else:
                st.error("ไม่พบข้อมูล")

    st.markdown("---")
    st.subheader("ข้อมูลพัสดุในระบบ (จัดเรียงแล้ว)")
    if st.button("แสดงข้อมูล (Sort)"):
        # ใช้ Sort ของคุณตามจำนวนข้อมูล
        temp_list = st.session_state.tracking_list.copy()
        if len(temp_list) > 0:
            if len(temp_list) < 43:
                st.info("ใช้ Insertion Sort")
                sorted_ids = insertionSort(temp_list)
            else:
                st.info("ใช้ Merge Sort")
                sorted_ids = mergeSort(temp_list)
            
            # วนลูปดึงข้อมูลจาก DB ตามรหัสที่เรียงแล้ว
            for t_id in sorted_ids:
                data = st.session_state.parcels_db[t_id]
                st.write(f"**รหัส:** {t_id} | **ผู้รับ:** {data['name']} | **ปลายทาง:** {data['dest']} | **สถานะ:** {data['status']}")
        else:
            st.write("ยังไม่มีข้อมูล")

with tab3:
    st.subheader("ค้นหาเส้นทางที่สั้นที่สุด")
    start_node = st.selectbox("จุดเริ่มต้น", list(G.nodes()), key="g_start")
    end_node = st.selectbox("ปลายทาง", list(G.nodes()), key="g_end")
    if st.button("คำนวณเส้นทาง"):
        try:
            path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
            dist = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
            st.success(f"ระยะทางรวม: {dist} กิโลเมตร")
            st.write("เส้นทาง: " + " ➔ ".join(path))
        except:
            st.error("ไม่สามารถคำนวณเส้นทางได้")
