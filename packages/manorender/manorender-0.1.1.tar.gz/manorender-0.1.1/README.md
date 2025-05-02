# ManoRender - Advanced 3D Rendering Engine

ManoRender is a powerful and flexible 3D rendering engine built with Python. It provides a comprehensive set of tools for creating, manipulating, and rendering 3D scenes.

## Features

- Advanced 3D Object Rendering
- Scene Management
- Camera Control
- Lighting System
- Material System
- Real-time Rendering
- GUI Support
- Web-based Rendering
- Error Handling
- Entity System
- Physics Integration
- Shader Support
- Texture Management

## Installation

```bash
# Install basic requirements
pip install -r renderer.mano

# Install development tools (optional)
pip install manorender[dev]

# Install documentation tools (optional)
pip install manorender[docs]
```

## Usage

```python
from manorender import ManoRender

# Create a new renderer
renderer = ManoRender()

# Create a new scene
scene = renderer.scene_new("main_scene")

# Camera settings
renderer.camera_new(0, 0, 10, 0, 0, 0)

# Add light
renderer.add_light(position=(0, 0, 10), color=(1, 1, 1))

# Entity operations
entity = renderer.sins_entity("main_entity")
entity.move(1, 2, 3).rotate(0, 45, 0).scale(2, 2, 2)

# Start rendering
renderer.render_start()
renderer.render(scene)
renderer.complete_ren()
```

## Advanced Features

### Error Handling
```python
# Check for errors
entity.add_error("Test error")
renderer.command_line("main_entity")
entity.clear_errors()
```

### Entity Management
```python
# Create and destroy entities
entity = renderer.sins_entity("entity1")
# ... do something with entity ...
renderer.point_entity("entity1")
```

### Physics Integration
```python
# Add physics properties
entity.physics.mass = 1.0
entity.physics.friction = 0.5
entity.physics.restitution = 0.8
```

## Development

The project is actively developed and new features are continuously being added. We welcome contributions from the community.

## Documentation

Project Documentation Deleted.

## Support

Contact from profile and search for debug.

## Texture Kullanımı

Texture'ları kullanmak için şu adımları takip edin:

1. Texture'ı yükle:
```python
# Temel texture yükleme
renderer.get_texture("wood_texture", "wood.png")

# Gelişmiş texture yükleme
renderer.get_texture(
    id="wood_texture",
    file="wood.png",
    mipmaps=True,          # Mipmapping etkin
    anisotropic=True,      # Anizotropik filtreleme etkin
    compression=True,      # Texture sıkıştırma etkin
    srgb=True             # sRGB renk uzayı etkin
)
```

2. Objeye texture uygula:
```python
# Temel texture uygulama
renderer.set_texture("wood_texture", "cube")

# Gelişmiş texture uygulama
renderer.set_texture(
    id="wood_texture",
    object="cube",
    uv_scale=2.0,        # UV ölçeklendirme
    uv_offset=(0.5, 0.5),# UV kaydırma
    repeat=True,         # Tekrarlama etkin
    clamp=False          # Kenar kırma etkin
)
```

## Gelişmiş Texture Özellikleri

### Texture Atlas
```python
# Texture atlas oluştur
renderer.create_texture_atlas(
    atlas_id="terrain_atlas",
    textures={
        "grass": (0, 0),
        "dirt": (512, 0),
        "rock": (0, 512)
    },
    size=(2048, 2048)
)
```

### Cubemap
```python
# Cubemap oluştur
renderer.create_cubemap(
    cubemap_id="skybox",
    faces={
        "right": "right.png",
        "left": "left.png",
        "top": "top.png",
        "bottom": "bottom.png",
        "front": "front.png",
        "back": "back.png"
    }
)
```

### Normal Map
```python
# Normal map oluştur
renderer.create_normal_map(
    id="normal_map",
    file="heightmap.png",
    strength=1.0
)
```

### Specular Map
```python
# Specular map oluştur
renderer.create_specular_map(
    id="specular_map",
    file="specular.png",
    glossiness=0.8
)
```

### Emissive Map
```python
# Emissive map oluştur
renderer.create_emissive_map(
    id="emissive_map",
    file="emissive.png",
    intensity=0.5
)
```

### Roughness Map
```python
# Roughness map oluştur
renderer.create_roughness_map(
    id="roughness_map",
    file="roughness.png",
    strength=0.7
)
```

### Parallax Map
```python
# Parallax map oluştur
renderer.create_parallax_map(
    id="parallax_map",
    file="heightmap.png",
    height=0.1,
    layers=8
)
```

### Displacement Map
```python
# Displacement map oluştur
renderer.create_displacement_map(
    id="displacement_map",
    file="displacement.png",
    strength=1.0
)
```

### Flow Map
```python
# Flow map oluştur
renderer.create_flow_map(
    id="flow_map",
    file="flow.png",
    speed=1.0
)
```

### Emissive Gradient
```python
# Emissive gradient oluştur
renderer.create_emissive_gradient(
    id="gradient",
    colors=[
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255)
    ],
    positions=[0.0, 0.5, 1.0]
)
```

### Procedural Texture
```python
# Yordamsal texture oluştur
renderer.create_procedural_texture(
    id="noise_texture",
    type="noise",
    parameters={
        "size": (1024, 1024),
        "octaves": 6,
        "persistence": 0.5,
        "lacunarity": 2.0,
        "scale": 1.0
    }
)
```

### Texture Animation
```python
# Texture animasyonu oluştur
renderer.create_texture_animation(
    id="animation",
    frames=[
        "frame1.png",
        "frame2.png",
        "frame3.png"
    ],
    fps=24
)

# Animasyonu güncelle
renderer.update_texture_animation("animation")
```

### Texture Filter
```python
# Blur filtresi oluştur
renderer.create_texture_filter(
    id="blur_filter",
    type="blur",
    parameters={
        "size": 3,
        "sigma": 1.0
    }
)

# Texture'e filtre uygula
renderer.apply_texture_filter("blur_filter", "texture_id")
```

### Texture Composite
```python
# Texture bileşimi oluştur
renderer.create_texture_composite(
    id="composite",
    textures=["texture1", "texture2"],
    blend_mode="add",
    opacity=1.0
)
```

### Texture Mask
```python
# Texture maskesi oluştur
renderer.create_texture_mask(
    id="masked_texture",
    mask_file="mask.png",
    texture_file="texture.png"
)
```

### Texture Array
```python
# Texture dizisi oluştur
renderer.create_texture_array(
    id="texture_array",
    textures=["tex1", "tex2", "tex3"],
    layers=3
)
```

### Cubemap Array
```python
# Cubemap dizisi oluştur
renderer.create_cubemap_array(
    id="cubemap_array",
    cubemaps=["cubemap1", "cubemap2"],
    layers=2
)

## License

Plazma Licence
Local Projects
Avaible Projects
Setupable Projects
Line up!
<profile> Engine </profile>


