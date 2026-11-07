// Compress the GLBs exported by blender/build.py into public/models (meshopt + quantization).
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, flatten, join, meshopt, prune, quantize, weld } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { readdir, stat } from 'node:fs/promises';
import path from 'node:path';

await MeshoptEncoder.ready;
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });
const src = 'blender/out', dst = 'public/models';
for (const f of (await readdir(src)).filter((f) => f.endsWith('.glb'))) {
  const doc = await io.read(path.join(src, f));
  await doc.transform(dedup(), weld(), prune(), quantize({ quantizeNormal: 10, quantizePosition: 14 }), meshopt({ encoder: MeshoptEncoder, level: 'high' }));
  const out = path.join(dst, f);
  await io.write(out, doc);
  console.log(f, ((await stat(path.join(src, f))).size / 1024).toFixed(0) + ' KB ->', ((await stat(out)).size / 1024).toFixed(0) + ' KB');
}
