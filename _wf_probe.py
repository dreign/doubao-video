import json, glob, os, collections

WF = r"C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI\user\default\workflows"
KEY = ('H3', 'flux2', 'minimax_h3_image', '整合')

for f in sorted(glob.glob(os.path.join(WF, '*.json'))):
    n = os.path.basename(f)
    if not any(k in n for k in KEY):
        continue
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print(n, '解析失败', e)
        continue
    nodes = d.get('nodes', [])
    types = collections.Counter(x.get('type') for x in nodes)
    mods, nums = [], []
    for x in nodes:
        for v in (x.get('widgets_values') or []):
            if isinstance(v, str) and v.endswith(('.safetensors', '.gguf', '.ckpt')):
                mods.append(v)
            if isinstance(v, int) and 1 <= v <= 3000:
                nums.append((x.get('type'), v))
    print('==', n, '节点', len(nodes))
    print('   类型:', dict(types.most_common(14)))
    print('   模型:', sorted(set(mods))[:8])
    print('   数值:', sorted(set(nums))[:12])
