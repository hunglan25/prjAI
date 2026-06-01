import os
import requests
import json
from collections import defaultdict 

def save_result_to_file(result, file_path):
    list1Ways_formatted = [f"[{', '.join(map(str, way))}]" for way in result["list1Ways"]]
    listLinks_formatted = [f"[{', '.join(map(str, link))}]" for link in result["listLinks"]]
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write('{\n')
        f.write(f'    "center": {json.dumps(result["center"], ensure_ascii=False)},\n')
        f.write(f'    "listBoundaries": [\n')
        f.write(',\n'.join([f'        {json.dumps(boundary, ensure_ascii=False)}' for boundary in result["listBoundaries"]]))
        f.write('\n    ],\n')
        f.write(f'    "listNodes": [\n')
        f.write(',\n'.join([f'        {json.dumps(node, ensure_ascii=False)}' for node in result["listNodes"]]))
        f.write('\n    ],\n')
        f.write(f'    "list1Ways": [\n        ')
        f.write(',\n        '.join(list1Ways_formatted))
        f.write('\n    ],\n')
        f.write(f'    "listLinks": [\n        ')
        f.write(',\n        '.join(listLinks_formatted))
        f.write('\n    ]\n')
        f.write('}\n')

url = "https://overpass-api.de/api/interpreter"

# Định nghĩa khung tọa độ (Bounding Box) bao quanh khu vực Lăng Bác
# Cú pháp: (Nam, Tây, Bắc, Đông) tương đương (min_lat, min_lng, max_lat, max_lng)
bbox = "21.0250,105.8200,21.0450,105.8500"

# Cú pháp truy vấn Overpass theo tọa độ thay vì tên phường
query = f"""
[out:json];
(
  way[highway]["highway"!~"footway|path|cycleway|pedestrian|steps"]({bbox});
);
(._;>;);
out body;
"""

print("Đang tải dữ liệu từ OpenStreetMap (Khu vực Lăng Bác)...")

headers = {
    "User-Agent": "hust-soict-map-project/1.0"
}

response = requests.post(url, data={"data": query}, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    nodes = {}
    ways = []

    for element in data["elements"]:
        if element["type"] == "node":
            nodes[element["id"]] = {"lat": element["lat"], "lng": element["lon"]}
        elif element["type"] == "way":
            ways.append(element)

    # 1. Gán cứng Center là tâm của Lăng Bác để bản đồ lấy làm mốc
    center = {"lat": 21.0368, "lng": 105.8346}

    # 2. Tạo đường viền giả (hình chữ nhật dựa trên bbox) để giao diện map có thể vẽ đường bao
    listBoundaries = [
        {"lat": 21.0300, "lng": 105.8280},
        {"lat": 21.0300, "lng": 105.8420},
        {"lat": 21.0420, "lng": 105.8420},
        {"lat": 21.0420, "lng": 105.8280},
        {"lat": 21.0300, "lng": 105.8280}  # Nối về điểm bắt đầu để khép kín hình
    ]

    # 3. Lọc ra các điểm giao cắt để xây dựng đồ thị đường đi
    node_ways_map = defaultdict(set)
    for way in ways:
        if "nodes" in way:
            for node_id in way["nodes"]:
                node_ways_map[node_id].add(way["id"])

    intersection_nodes = {node_id: {"lat": nodes[node_id]["lat"], "lng": nodes[node_id]["lng"]}
                          for node_id, ways_set in node_ways_map.items() if len(ways_set) > 1}

    listNodes = list(intersection_nodes.values())
    node_index = {node_id: i for i, node_id in enumerate(intersection_nodes.keys())}

    # 4. Trích xuất đường 1 chiều và các đường liên kết (Links)
    list1Ways = []
    adjacency_list = defaultdict(list)

    for way in ways:
        if "nodes" in way:
            is_oneway = way.get("tags", {}).get("oneway", "no") == "yes"
            previous_node = None
    
            for node_id in way["nodes"]:
                if node_id in intersection_nodes:
                    if previous_node is not None:
                        from_index = node_index[previous_node]
                        to_index = node_index[node_id]
                        if is_oneway:
                            list1Ways.append([from_index, to_index])
                            adjacency_list[from_index].append(to_index)
                        else:
                            adjacency_list[from_index].append(to_index)
                            adjacency_list[to_index].append(from_index)
                    previous_node = node_id

    listLinks = [list(dict.fromkeys(adjacency_list[i])) for i in range(len(listNodes))]

    # Đóng gói và xuất file
    result = {
        "center": center,
        "listBoundaries": listBoundaries,
        "listNodes": listNodes,
        "list1Ways": list1Ways,
        "listLinks": listLinks,
    }

    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "lang_bac_data.json")
    save_result_to_file(result, file_path)

    print(f"Thành công! Đã quét được {len(listNodes)} điểm giao cắt. Dữ liệu lưu vào: {file_path}")
else:
    print(f"Lỗi khi lấy dữ liệu từ API: {response.status_code} - {response.text}")
