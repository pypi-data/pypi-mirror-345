import argparse
from manorender import ManoRender

def main():
    parser = argparse.ArgumentParser(
        description='ManoRender - 3B Render Kütüphanesi'
    )
    
    # Alt komutlar için alt-parser oluşturma
    subparsers = parser.add_subparsers(dest='command')
    
    # Render komutu
    render_parser = subparsers.add_parser('render', help='Sahneyi render et')
    render_parser.add_argument('--scene', required=True, help='Render edilecek sahne dosyası')
    render_parser.add_argument('--width', type=int, default=800, help='Çıktı genişliği')
    render_parser.add_argument('--height', type=int, default=600, help='Çıktı yüksekliği')
    
    # Sahne komutu
    scene_parser = subparsers.add_parser('scene', help='Sahne işlemleri')
    scene_parser.add_argument('--create', help='Yeni sahne oluştur')
    scene_parser.add_argument('--list', action='store_true', help='Mevcut sahneleri listele')
    
    args = parser.parse_args()
    
    if args.command == 'render':
        renderer = ManoRender()
        scene = renderer.create_scene()
        renderer.render(scene, width=args.width, height=args.height)
    elif args.command == 'scene':
        if args.list:
            print("Mevcut sahneler:")
            # Sahneleri listeleme kodu buraya gelecek
        elif args.create:
            print(f"Yeni sahne oluşturuldu: {args.create}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
