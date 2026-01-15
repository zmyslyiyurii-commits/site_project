document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("file");
    const fileLabel = fileInput.parentElement;
    const canvas = document.getElementById("previewCanvas");
    const ctx = canvas.getContext("2d");
    const scaleSlider = document.getElementById("scaleSlider");
    const toast = document.getElementById("toast");

    let img = new Image();
    let scale = 1, rotateDeg = 0, flipped = false, currentFilter = "none";

    let drawingMode = false;
    let drawing = false;
    let lines = []; // Масив ліній
    let currentLine = [];

    const drawBtn = document.getElementById("drawBtn");

    function showToast(text){
        toast.textContent = text;
        toast.style.display = "block";
        setTimeout(() => toast.style.display = "none", 2000);
    }

    // --- Малювання картинки та ліній ---
    function drawAll(){
        if(!img.src) return;

        // Розміри canvas
        let w = img.width * scale;
        let h = img.height * scale;
        if(rotateDeg % 180 !== 0){
            canvas.width = h;
            canvas.height = w;
        } else {
            canvas.width = w;
            canvas.height = h;
        }

        ctx.clearRect(0,0,canvas.width,canvas.height);

        // Малюємо фото
        ctx.save();
        ctx.filter = currentFilter;
        ctx.translate(canvas.width/2, canvas.height/2);
        ctx.rotate(rotateDeg * Math.PI/180);
        ctx.scale(flipped ? -scale : scale, scale);
        ctx.drawImage(img, -img.width/2, -img.height/2);
        ctx.restore();

        // Малюємо всі лінії
        lines.forEach(line => {
            drawLine(line);
        });

        // Малюємо поточну лінію, якщо малюємо
        if(currentLine.length > 0) drawLine(currentLine);
    }

    function drawLine(line){
        if(line.length < 2) return;
        ctx.save();
        ctx.strokeStyle = "red";
        ctx.lineWidth = 3; // товщина лінії
        ctx.lineJoin = "round";
        ctx.lineCap = "round";
        ctx.beginPath();
        const start = imageToCanvas(line[0]);
        ctx.moveTo(start.x, start.y);
        for(let i=1; i<line.length; i++){
            const p = imageToCanvas(line[i]);
            ctx.lineTo(p.x, p.y);
        }
        ctx.stroke();
        ctx.restore();
    }

    // --- Перетворення координат зображення -> canvas ---
    function imageToCanvas(p){
        let x = p.x;
        let y = p.y;
        if(flipped) x = -x;

        let rad = rotateDeg * Math.PI/180;
        let cos = Math.cos(rad);
        let sin = Math.sin(rad);

        const cx = x * cos - y * sin;
        const cy = x * sin + y * cos;

        return {
            x: cx * scale + canvas.width/2,
            y: cy * scale + canvas.height/2
        };
    }

    // --- Перетворення координат canvas -> зображення ---
    function canvasToImage(cx, cy){
        let x = (cx - canvas.width/2)/scale;
        let y = (cy - canvas.height/2)/scale;

        let rad = -rotateDeg * Math.PI/180;
        let cos = Math.cos(rad);
        let sin = Math.sin(rad);

        let ix = x * cos - y * sin;
        let iy = x * sin + y * cos;

        if(flipped) ix = -ix;

        return {x: ix, y: iy};
    }

    // --- Завантаження фото ---
    fileInput.addEventListener("change", e => {
        const file = e.target.files[0];
        if(!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
            img.src = ev.target.result;
            img.onload = () => {
                scale = 1; rotateDeg = 0; flipped = false; currentFilter = "none";
                scaleSlider.value = 1;
                canvas.style.display = "block";
                scaleSlider.style.display = "block";
                fileLabel.style.display = "none";
                lines = [];
                currentLine = [];
                drawAll();
                showToast("Фото завантажено");
            };
        };
        reader.readAsDataURL(file);
    });

    // --- Масштаб ---
    scaleSlider.min = 0.1;
    scaleSlider.max = 4;
    scaleSlider.step = 0.01;
    scaleSlider.addEventListener("input", () => {
        scale = parseFloat(scaleSlider.value);
        drawAll();
    });

    // --- Кнопки ---
    document.getElementById("rotateBtn").onclick = () => { rotateDeg=(rotateDeg+90)%360; drawAll(); };
    document.getElementById("flipBtn").onclick = () => { flipped=!flipped; drawAll(); };
    document.getElementById("bwBtn").onclick = () => { currentFilter="grayscale(100%)"; drawAll(); };
    document.getElementById("sepiaBtn").onclick = () => { currentFilter="sepia(100%)"; drawAll(); };
    document.getElementById("contrastBtn").onclick = () => { currentFilter="contrast(150%)"; drawAll(); };
    document.getElementById("brightnessBtn").onclick = () => { currentFilter="brightness(140%)"; drawAll(); };
    document.getElementById("saturateBtn").onclick = () => { currentFilter="saturate(150%)"; drawAll(); };
    document.getElementById("invertBtn").onclick = () => { currentFilter="invert(100%)"; drawAll(); };

    document.getElementById("resetBtn").onclick = () => {
        scale = 1; rotateDeg = 0; flipped = false; currentFilter = "none";
        scaleSlider.value = 1;
        canvas.style.display = "none";
        scaleSlider.style.display = "none";
        fileLabel.style.display = "flex";
        fileInput.value = "";
        lines = [];
        currentLine = [];
        ctx.clearRect(0,0,canvas.width,canvas.height);
        showToast("Фото скинуто");
    };

    document.getElementById("downloadBtn").onclick = () => {
        if(!img.src) return;
        const link = document.createElement("a");
        link.download = "edited_image.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    };

    // --- Режим малювання ---
    drawBtn.onclick = () => {
        drawingMode = !drawingMode;
        drawBtn.style.background = drawingMode ? "#27ae60" : "#2980b9";
    };

    function getCursorPos(e){
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.onmousedown = (e) => {
        if(!drawingMode) return;
        drawing = true;
        currentLine = [];
        currentLine.push(canvasToImage(getCursorPos(e).x, getCursorPos(e).y));
        drawAll();
    };
    canvas.onmousemove = (e) => {
        if(drawing && drawingMode){
            currentLine.push(canvasToImage(getCursorPos(e).x, getCursorPos(e).y));
            drawAll();
        }
    };
    canvas.onmouseup = () => {
        if(drawing && drawingMode){
            lines.push(currentLine);
            currentLine = [];
        }
        drawing = false;
    };
});
