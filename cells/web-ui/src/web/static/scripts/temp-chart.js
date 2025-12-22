import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- 1. LÓGICA PARA EL GRÁFICO 3D ---
const container = document.getElementById('plot-container');
const tooltip = document.getElementById('tooltip');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x262626);

const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 2000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
container.insertBefore(renderer.domElement, container.firstChild);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.autoRotate = false;
controls.autoRotateSpeed = 0.5;

scene.add(new THREE.AmbientLight(0xffffff, 1.2));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
dirLight.position.set(10, 20, 15);
scene.add(dirLight);

const loader = new GLTFLoader();
let currentModel = null;
let isFirstLoad = true;

function fitCameraToScene(object) {
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= 1.2;
    camera.position.set(center.x, center.y, center.z + cameraZ);
    controls.target.copy(center);
    controls.update();
}

function onWindowResize() {
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}
window.addEventListener('resize', onWindowResize);

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

container.addEventListener('mousemove', (event) => {
    const rect = container.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const intersect = intersects[0];
        const obj = intersect.object;
        let tooltipText = '';

        if (obj.name === 'battery_pack' && obj.userData.temperatures) {
            if (intersect.face) {
                const face = intersect.face;
                const temps = obj.userData.temperatures;
                const pointTemp = (temps[face.a] + temps[face.b] + temps[face.c]) / 3.0;
                tooltipText = `Temperatura: ${pointTemp.toFixed(2)} °C`;
            } else {
                tooltipText = `Batería (info no disponible)`;
            }
        } else if (obj.name.startsWith('sensor_') && obj.userData.sensorInfo) {
            const temp = obj.userData.sensorInfo.temp;
            tooltipText = `${obj.name}: ${temp.toFixed(2)} °C`;
        }

        if (tooltipText) {
            tooltip.style.display = 'block';
            tooltip.style.left = `${event.clientX - rect.left + 15}px`;
            tooltip.style.top = `${event.clientY - rect.top}px`;
            tooltip.innerHTML = tooltipText;
        } else {
            tooltip.style.display = 'none';
        }
    } else {
        tooltip.style.display = 'none';
    }
});

window.update3dGraph = (modelUrl, meshTemp, sensorData) => {
    if (currentModel) {
        scene.remove(currentModel);
    }
    loader.load(modelUrl, (gltf) => {
        currentModel = gltf.scene;
        const meshes = [];
        currentModel.traverse((child) => { if (child.isMesh) { meshes.push(child); } });

        if (meshes.length > 0) {
            meshes[0].name = 'battery_pack';
            meshes[0].userData.temperatures = meshTemp;
        }
        if (meshes.length > 1) {
            for (let i = 1; i < meshes.length; i++) {
                const sensorIndex = i - 1;
                if (sensorData && sensorData[sensorIndex]) {
                    meshes[i].name = `sensor_${sensorIndex}`;
                    meshes[i].userData.sensorInfo = sensorData[sensorIndex];
                }
            }
        }
        scene.add(currentModel);
        if (isFirstLoad) {
            fitCameraToScene(currentModel);
            isFirstLoad = false;
        }
    });
};