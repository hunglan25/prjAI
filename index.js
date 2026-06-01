let map = map_build(id='map');
let findPath = document.getElementById('find-path').value;
let dummyTSP = document.getElementById('dummy-TSP').value;
let mandatory = parseInt(document.getElementById('mandatory-point').value);
clickMAX = mandatory + 2;

handleMapClick(map);
document.getElementById('show-map').addEventListener("click", () => showMap(map));
document.getElementById('mandatory-point').addEventListener("change", () => reset(map));

// SỰ KIỆN CLICK NÚT RUN
document.getElementById('run').addEventListener("click", () => {
    
    // Bật Loading Spinner
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) loadingOverlay.classList.remove('hidden');

    // Dùng setTimeout để giao diện kịp hiển thị Loading trước khi CPU tính toán nặng
    setTimeout(() => {
        initGraph();
        findPath = document.getElementById('find-path').value;
        dummyTSP = document.getElementById('dummy-TSP').value;

        const start = window.performance.now();

        // Chạy thuật toán tìm đường
        let { distance, path } = 
            (parseInt(findPath) === 0) ? Floyd_Warshall(parseInt(dummyTSP)) :
            (parseInt(findPath) === 1) ? Dijkstra(parseInt(dummyTSP)) : 
            (parseInt(findPath) === 2) ? A_Star(parseInt(dummyTSP)) :
            (parseInt(findPath) === 3) ? BFS(parseInt(dummyTSP)) :
            (parseInt(findPath) === 4) ? DFS(parseInt(dummyTSP)) :
            (parseInt(findPath) === 5) ? BellmanFord(parseInt(dummyTSP)) :
            (parseInt(findPath) === 6) ? Greedy1(parseInt(dummyTSP)):
            (parseInt(findPath) === 7) ? UniformCostSearch(parseInt(dummyTSP)):
            (parseInt(findPath) === 8) ? Johnson(parseInt(dummyTSP)):
            // (parseInt(findPath) === 9) ? IDDFS(parseInt(dummyTSP)):
                                        { distance: null, path: null } ;
        
        const end = window.performance.now();
        const executionTime = end - start; // Đã xóa dòng lặp lỗi

        console.log('time: ', executionTime, 'ms');
        console.log('path: ', path);
        console.log('distance: ', distance);

        // Tắt Loading Spinner sau khi có kết quả
        if (loadingOverlay) loadingOverlay.classList.add('hidden');

        // Bẫy lỗi đứt gãy đồ thị
        if (distance == null || distance > 90000) {
            alert("⚠️ Không tìm thấy đường đi! Hai điểm này nằm trên các đoạn đường bị đứt gãy hoặc ngõ cụt. Vui lòng chọn điểm khác.");
            return; 
        }

        // Định dạng số liệu hiển thị
        let formatDistance = distance < 1 
            ? (distance * 1000).toFixed(0) + " mét" 
            : distance.toFixed(2) + " km";

        let formatTime = executionTime < 1 
            ? "< 1 ms" 
            : executionTime.toFixed(0) + " ms";

        // In bảng kết quả
        document.getElementById('console').innerHTML = 
        `<table>
            <tr>
                <th>Tổng quãng đường</th>
                <th>Thời gian xử lý</th>
                <th>Số điểm đi qua</th>
            </tr>
            <tr>
                <td style="color: #10b981; font-weight: bold;">${formatDistance}</td>
                <td style="color: #3b82f6; font-weight: bold;">${formatTime}</td>
                <td>${path.length} điểm nút</td>
            </tr>
         </table>`;

        // Vẽ đường đi lên bản đồ
        if(distance < 9) {
            showPath(path, true);
        }
    }, 50); // <<< CHÍNH XÁC: Đóng hàm setTimeout ở đây!
});