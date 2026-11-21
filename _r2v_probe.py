import json
f = r"C:\Users\Administrator\ComfyUI-Installs\ComfyUI\ComfyUI\user\default\workflows\MINIMAX-H3_多图参考生视频.json"
d = json.load(open(f, encoding='utf-8'))
for n in d.get('nodes', []):
    if n.get('type', '').startswith('MiniMaxH3') or n.get('type') in ('BasicScheduler', 'LoraLoaderModelOnly', 'ResolutionSelector', 'PrimitiveFloat', 'SamplerCustomAdvanced'):
        print('-', n.get('type'), '|', json.dumps(n.get('widgets_values'), ensure_ascii=False)[:300])
print('--- links ---')
for l in d.get('links', [])[:0]:
    pass
for n in d.get('nodes', []):
    if n.get('type') == 'MiniMaxH3ReferenceToVideo':
        print(json.dumps(n, ensure_ascii=False)[:1200])
