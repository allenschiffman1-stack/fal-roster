// Build a minimal GLB humanoid placeholder per character.
// Six boxes: head, torso, two arms, two legs. Single material w/ accent color.
// Output: assets/glb/<name>.glb and assets/companions/<name>.glb (companions = smaller).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = path.resolve(path.dirname(__filename), "..", "..");

const CHARACTERS = [
  ["master-chief", "#5B8C5A"],
  ["kratos", "#C0392B"],
  ["link", "#27AE60"],
  ["mario", "#E74C3C"],
  ["samus", "#E67E22"],
  ["cloud", "#2C3E50"],
  ["snake", "#2C3E50"],
  ["geralt", "#7F8C8D"],
  ["aloy", "#E74C3C"],
  ["lara", "#5D4E37"],
  ["arthur", "#8B4513"],
  ["joel", "#5D4E37"],
];

function hexToRgb(hex) {
  const n = parseInt(hex.replace("#", ""), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => v / 255);
}

// Build a box as 24 verts (so each face has its own normal) + 36 indices.
function boxGeom(cx, cy, cz, sx, sy, sz) {
  const hx = sx / 2, hy = sy / 2, hz = sz / 2;
  // Six faces: +X,-X,+Y,-Y,+Z,-Z. Each: 4 verts + 2 tris.
  const faces = [
    { n: [1, 0, 0], v: [[+hx, -hy, -hz], [+hx, +hy, -hz], [+hx, +hy, +hz], [+hx, -hy, +hz]] },
    { n: [-1, 0, 0], v: [[-hx, -hy, +hz], [-hx, +hy, +hz], [-hx, +hy, -hz], [-hx, -hy, -hz]] },
    { n: [0, 1, 0], v: [[-hx, +hy, -hz], [-hx, +hy, +hz], [+hx, +hy, +hz], [+hx, +hy, -hz]] },
    { n: [0, -1, 0], v: [[-hx, -hy, +hz], [-hx, -hy, -hz], [+hx, -hy, -hz], [+hx, -hy, +hz]] },
    { n: [0, 0, 1], v: [[-hx, -hy, +hz], [+hx, -hy, +hz], [+hx, +hy, +hz], [-hx, +hy, +hz]] },
    { n: [0, 0, -1], v: [[+hx, -hy, -hz], [-hx, -hy, -hz], [-hx, +hy, -hz], [+hx, +hy, -hz]] },
  ];
  const positions = [];
  const normals = [];
  const indices = [];
  let base = 0;
  for (const f of faces) {
    for (const v of f.v) {
      positions.push(v[0] + cx, v[1] + cy, v[2] + cz);
      normals.push(...f.n);
    }
    indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
    base += 4;
  }
  return { positions, normals, indices };
}

function mergeGeoms(geoms) {
  const positions = [];
  const normals = [];
  const indices = [];
  let vOffset = 0;
  for (const g of geoms) {
    positions.push(...g.positions);
    normals.push(...g.normals);
    for (const i of g.indices) indices.push(i + vOffset);
    vOffset += g.positions.length / 3;
  }
  return { positions, normals, indices };
}

// Humanoid (small/big variant for companion vs hero).
function humanoid(scale = 1) {
  const s = scale;
  return mergeGeoms([
    boxGeom(0, 1.55 * s, 0, 0.45 * s, 0.45 * s, 0.45 * s),    // head
    boxGeom(0, 0.85 * s, 0, 0.85 * s, 1.0 * s, 0.45 * s),     // torso
    boxGeom(-0.55 * s, 0.85 * s, 0, 0.25 * s, 0.95 * s, 0.25 * s), // L arm
    boxGeom(+0.55 * s, 0.85 * s, 0, 0.25 * s, 0.95 * s, 0.25 * s), // R arm
    boxGeom(-0.22 * s, -0.05 * s, 0, 0.32 * s, 0.95 * s, 0.32 * s), // L leg
    boxGeom(+0.22 * s, -0.05 * s, 0, 0.32 * s, 0.95 * s, 0.32 * s), // R leg
  ]);
}

function pad4(buf) {
  const rem = buf.length % 4;
  if (rem === 0) return buf;
  return Buffer.concat([buf, Buffer.alloc(4 - rem)]);
}

function buildGLB(geom, color) {
  // Build binary buffer: float32 positions, float32 normals, uint16 indices.
  const positions = new Float32Array(geom.positions);
  const normals = new Float32Array(geom.normals);
  const indices = new Uint16Array(geom.indices);

  // Compute bounds.
  let minP = [Infinity, Infinity, Infinity];
  let maxP = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < positions.length; i += 3) {
    for (let j = 0; j < 3; j++) {
      if (positions[i + j] < minP[j]) minP[j] = positions[i + j];
      if (positions[i + j] > maxP[j]) maxP[j] = positions[i + j];
    }
  }

  // Pack into single binary chunk with 4-byte alignment between sections.
  const posBuf = Buffer.from(positions.buffer, positions.byteOffset, positions.byteLength);
  const normBuf = Buffer.from(normals.buffer, normals.byteOffset, normals.byteLength);
  const idxBuf = pad4(Buffer.from(indices.buffer, indices.byteOffset, indices.byteLength));

  const posOffset = 0;
  const normOffset = posBuf.length;
  const idxOffset = normOffset + normBuf.length;
  const binaryLength = idxOffset + idxBuf.length;
  const binary = Buffer.concat([posBuf, normBuf, idxBuf], binaryLength);

  const gltf = {
    asset: { version: "2.0", generator: "fal-roster placeholder gen" },
    scene: 0,
    scenes: [{ nodes: [0] }],
    nodes: [{ mesh: 0 }],
    meshes: [
      {
        primitives: [
          {
            attributes: { POSITION: 0, NORMAL: 1 },
            indices: 2,
            material: 0,
          },
        ],
      },
    ],
    materials: [
      {
        name: "accent",
        pbrMetallicRoughness: {
          baseColorFactor: [...color, 1.0],
          metallicFactor: 0.15,
          roughnessFactor: 0.55,
        },
      },
    ],
    bufferViews: [
      { buffer: 0, byteOffset: posOffset, byteLength: posBuf.length, target: 34962 },
      { buffer: 0, byteOffset: normOffset, byteLength: normBuf.length, target: 34962 },
      { buffer: 0, byteOffset: idxOffset, byteLength: indices.byteLength, target: 34963 },
    ],
    accessors: [
      {
        bufferView: 0,
        componentType: 5126, // FLOAT
        count: positions.length / 3,
        type: "VEC3",
        min: minP,
        max: maxP,
      },
      {
        bufferView: 1,
        componentType: 5126,
        count: normals.length / 3,
        type: "VEC3",
      },
      {
        bufferView: 2,
        componentType: 5123, // UNSIGNED_SHORT
        count: indices.length,
        type: "SCALAR",
      },
    ],
    buffers: [{ byteLength: binaryLength }],
  };

  const json = JSON.stringify(gltf);
  const jsonBuf = pad4(Buffer.from(json, "utf8"));
  const binChunkBuf = binary; // already padded

  // GLB header: magic(4) version(4) totalLen(4) + 2 chunks (header 8 each)
  const totalLen = 12 + 8 + jsonBuf.length + 8 + binChunkBuf.length;
  const header = Buffer.alloc(12);
  header.writeUInt32LE(0x46546c67, 0); // glTF
  header.writeUInt32LE(2, 4);
  header.writeUInt32LE(totalLen, 8);

  const jsonChunkHeader = Buffer.alloc(8);
  jsonChunkHeader.writeUInt32LE(jsonBuf.length, 0);
  jsonChunkHeader.writeUInt32LE(0x4e4f534a, 4); // JSON

  const binChunkHeader = Buffer.alloc(8);
  binChunkHeader.writeUInt32LE(binChunkBuf.length, 0);
  binChunkHeader.writeUInt32LE(0x004e4942, 4); // BIN

  return Buffer.concat([header, jsonChunkHeader, jsonBuf, binChunkHeader, binChunkBuf]);
}

function main() {
  const heroDir = path.join(ROOT, "assets", "glb");
  const compDir = path.join(ROOT, "assets", "companions");
  fs.mkdirSync(heroDir, { recursive: true });
  fs.mkdirSync(compDir, { recursive: true });

  for (const [name, hex] of CHARACTERS) {
    const color = hexToRgb(hex);
    const heroGeom = humanoid(1.0);
    const compGeom = humanoid(0.55);
    const heroGlb = buildGLB(heroGeom, color);
    const compGlb = buildGLB(compGeom, color);
    fs.writeFileSync(path.join(heroDir, `${name}.glb`), heroGlb);
    fs.writeFileSync(path.join(compDir, `${name}.glb`), compGlb);
    console.log(`${name}: hero=${heroGlb.length}b comp=${compGlb.length}b`);
  }
}

main();
