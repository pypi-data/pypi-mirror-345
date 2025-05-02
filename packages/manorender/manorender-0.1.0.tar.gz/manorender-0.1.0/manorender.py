import numpy as np
from PIL import Image
import pythreejs as p3js
from IPython.display import display

class ManoRender:
    def __init__(self):
        """Render motorunun başlatıcısı"""
        self.scenes = {}
        self.current_scene = None
        self.camera = None
        self.lights = []
        
    def scene_new(self, name):
        """Yeni sahne oluşturur"""
        if name in self.scenes:
            raise ValueError(f"Sahne '{name}' zaten mevcut")
        scene = Scene()
        self.scenes[name] = scene
        self.current_scene = scene
        return scene
    
    def scene_pos(self, x, y, z):
        """Sahne pozisyonunu ayarlar"""
        if self.current_scene is None:
            raise ValueError("Aktif bir sahne yok")
        self.current_scene.position = np.array([x, y, z])
        return self.current_scene
    
    def scene_scale(self, x, y, z):
        """Sahne ölçeklendirmesini ayarlar"""
        if self.current_scene is None:
            raise ValueError("Aktif bir sahne yok")
        self.current_scene.scale = np.array([x, y, z])
        return self.current_scene
    
    def scene_rotate(self, x, y, z):
        """Sahne rotasyonunu ayarlar"""
        if self.current_scene is None:
            raise ValueError("Aktif bir sahne yok")
        self.current_scene.rotation = np.array([x, y, z])
        return self.current_scene
        
    def create_scene(self):
        """Yeni bir sahne oluşturur"""
        scene = Scene()
        self.scenes.append(scene)
        self.current_scene = scene
        return scene
    
    def camera_new(self, x, y, z, look_at_x, look_at_y, look_at_z):
        """Yeni kamera oluşturur"""
        self.camera = Camera(
            position=(x, y, z),
            look_at=(look_at_x, look_at_y, look_at_z)
        )
        return self.camera
    
    def camera_pos(self, x, y, z):
        """Kamera pozisyonunu ayarlar"""
        if self.camera is None:
            raise ValueError("Kamera oluşturulmamış")
        self.camera.position = np.array([x, y, z])
        return self.camera
    
    def camera_look_at(self, x, y, z):
        """Kamera bakış açısını ayarlar"""
        if self.camera is None:
            raise ValueError("Kamera oluşturulmamış")
        self.camera.look_at = np.array([x, y, z])
        return self.camera
    
    def fov_camera(self, exist):
        """Kamera görüş alanını ayarlar"""
        if self.camera is None:
            raise ValueError("Kamera oluşturulmamış")
        if exist:
            self.camera.fov = 75
        return self.camera
    
    def add_light(self, position=(0, 0, 10), color=(1, 1, 1)):
        """Sahneye ışık ekler"""
        light = Light(position, color)
        self.lights.append(light)
        return light
    
    def render_start(self):
        """Render işlemini başlatır"""
        self._rendering = True
        return self
    
    def render_complete(self):
        """Render işlemini tamamlar"""
        self._rendering = False
        return self
    
    def enable_audio(self, enable=True):
        """Ses sistemini etkinleştirir/devre dışı bırakır"""
        self._audio_enabled = enable
        return self
    
    def set_audio_device(self, device_id):
        """Ses cihazını ayarlar"""
        if device_id in self._audio_devices:
            self._audio = self._audio_devices[device_id]
        return self
    
    def create_audio_source(self, position=(0, 0, 0), volume=1.0, pitch=1.0):
        """Yeni bir ses kaynağı oluşturur"""
        source = {
            "position": np.array(position),
            "volume": volume,
            "pitch": pitch,
            "loop": False,
            "playing": False
        }
        self._audio_sources.append(source)
        return len(self._audio_sources) - 1
    
    def create_audio_listener(self, position=(0, 0, 0), forward=(0, 0, -1), up=(0, 1, 0)):
        """Yeni bir ses dinleyicisi oluşturur"""
        listener = {
            "position": np.array(position),
            "forward": np.array(forward),
            "up": np.array(up)
        }
        self._audio_listeners.append(listener)
        return len(self._audio_listeners) - 1
    
    def play_sound(self, source_id, file_path, loop=False):
        """Sesi oynatır"""
        if 0 <= source_id < len(self._audio_sources):
            source = self._audio_sources[source_id]
            source["playing"] = True
            source["loop"] = loop
            # Ses dosyasını yükle ve oynat
            # Bu metod daha sonra detaylı implementasyon alacak
        return self
    
    def stop_sound(self, source_id):
        """Sesi durdurur"""
        if 0 <= source_id < len(self._audio_sources):
            self._audio_sources[source_id]["playing"] = False
        return self
    
    def set_audio_volume(self, volume):
        """Genel ses hacmini ayarlar"""
        self._audio_volume = max(0.0, min(1.0, volume))
        return self
    
    def set_audio_balance(self, balance):
        """Ses bakiyesini ayarlar"""
        self._audio_balance = max(-1.0, min(1.0, balance))
        return self
    
    def set_audio_pitch(self, pitch):
        """Ses tonunu ayarlar"""
        self._audio_pitch = max(0.0, pitch)
        return self
    
    def enable_reverb(self, enable=True):
        """Reverb efektini etkinleştirir/devre dışı bırakır"""
        self._audio_reverb = enable
        return self
    
    def enable_compression(self, enable=True):
        """Kompresyon efektini etkinleştirir/devre dışı bırakır"""
        self._audio_compression = enable
        return self
    
    def enable_equalizer(self, enable=True):
        """Eşitleyici efektini etkinleştirir/devre dışı bırakır"""
        self._audio_equalizer = enable
        return self
    
    def enable_spatialization(self, enable=True):
        """Mekansal sesi etkinleştirir/devre dışı bırakır"""
        self._audio_spatialization = enable
        return self
    
    def enable_doppler(self, enable=True):
        """Doppler efektini etkinleştirir/devre dışı bırakır"""
        self._audio_doppler = enable
        return self
    
    def enable_occlusion(self, enable=True):
        """Occlusion efektini etkinleştirir/devre dışı bırakır"""
        self._audio_occlusion = enable
        return self
    
    def render(self, scene=None, width=800, height=600, quality=1.0, shadows=True, reflections=True, ambient_occlusion=True, motion_blur=False, depth_of_field=False, anti_aliasing=True, bloom=False, color_correction=False, lens_flare=False, volumetric_lighting=False, screen_space_reflections=False, temporal_anti_aliasing=False, adaptive_sampling=False):
        """Sahneyi render eder"""
        if scene is None:
            scene = self.current_scene
            
        if scene is None:
            raise ValueError("Render edilecek bir sahne seçilmedi")
            
        # Render kalitesini ayarla
        self._quality = quality
        self._shadows = shadows
        self._reflections = reflections
        self._ambient_occlusion = ambient_occlusion
        self._motion_blur = motion_blur
        self._depth_of_field = depth_of_field
        self._anti_aliasing = anti_aliasing
        self._bloom = bloom
        self._color_correction = color_correction
        self._lens_flare = lens_flare
        self._volumetric_lighting = volumetric_lighting
        self._screen_space_reflections = screen_space_reflections
        self._temporal_anti_aliasing = temporal_anti_aliasing
        self._adaptive_sampling = adaptive_sampling
        
        # Render parametrelerini hesapla
        self._calculate_render_parameters()
        
        # Temel render işlemi
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Her nesne için render işlemi
        for obj in scene.objects:
            self._render_object(obj, image)
            
        # Sonuçları görüntüle
        img = Image.fromarray(image)
        img.show()
        return img
    
    def _calculate_render_parameters(self):
        """Render parametrelerini hesaplar"""
        self._shadow_map_size = int(8192 * self._quality)
        self._reflection_quality = self._quality
        self._ao_samples = int(32 * self._quality)
        self._blur_samples = int(16 * self._quality)
        self._depth_samples = int(8 * self._quality)
        self._bloom_threshold = 1.0 + (1.0 - self._quality)
        self._color_correction_strength = self._quality
        self._lens_flare_intensity = self._quality * 0.5
        self._volumetric_samples = int(64 * self._quality)
        self._ssr_samples = int(32 * self._quality)
        self._taa_samples = int(16 * self._quality)
        self._adaptive_threshold = 0.01 * (1.0 - self._quality)
        
    def enable_bloom(self, enable=True):
        """Bloom etkisini etkinleştirir/devre dışı bırakır"""
        self._bloom = enable
        return self
    
    def enable_color_correction(self, enable=True):
        """Renk düzeltme etkisini etkinleştirir/devre dışı bırakır"""
        self._color_correction = enable
        return self
    
    def enable_lens_flare(self, enable=True):
        """Lens flare etkisini etkinleştirir/devre dışı bırakır"""
        self._lens_flare = enable
        return self
    
    def enable_volumetric_lighting(self, enable=True):
        """Volumetric lighting etkisini etkinleştirir/devre dışı bırakır"""
        self._volumetric_lighting = enable
        return self
    
    def enable_screen_space_reflections(self, enable=True):
        """Screen space reflections etkisini etkinleştirir/devre dışı bırakır"""
        self._screen_space_reflections = enable
        return self
    
    def enable_temporal_anti_aliasing(self, enable=True):
        """Temporal anti aliasing etkisini etkinleştirir/devre dışı bırakır"""
        self._temporal_anti_aliasing = enable
        return self
    
    def enable_adaptive_sampling(self, enable=True):
        """Adaptive sampling etkisini etkinleştirir/devre dışı bırakır"""
        self._adaptive_sampling = enable
        return self
    
    def set_bloom_threshold(self, threshold):
        """Bloom eşiğini ayarlar"""
        self._bloom_threshold = max(0.0, threshold)
        return self
    
    def set_color_correction_strength(self, strength):
        """Renk düzeltme gücünü ayarlar"""
        self._color_correction_strength = max(0.0, min(1.0, strength))
        return self
    
    def set_lens_flare_intensity(self, intensity):
        """Lens flare yoğunluğunu ayarlar"""
        self._lens_flare_intensity = max(0.0, intensity)
        return self
    
    def set_volumetric_samples(self, samples):
        """Volumetric örneklem sayısını ayarlar"""
        self._volumetric_samples = max(1, min(128, samples))
        return self
    
    def set_ssr_samples(self, samples):
        """Screen space reflections örneklem sayısını ayarlar"""
        self._ssr_samples = max(1, min(64, samples))
        return self
    
    def set_taa_samples(self, samples):
        """Temporal anti aliasing örneklem sayısını ayarlar"""
        self._taa_samples = max(1, min(32, samples))
        return self
    
    def set_adaptive_threshold(self, threshold):
        """Adaptive sampling eşiğini ayarlar"""
        self._adaptive_threshold = max(0.0, threshold)
        return self
    
    def _calculate_render_parameters(self):
        """Render parametrelerini hesaplar"""
        self._shadow_map_size = int(4096 * self._quality)
        self._reflection_quality = self._quality
        self._ao_samples = int(16 * self._quality)
        self._blur_samples = int(8 * self._quality)
        self._depth_samples = int(4 * self._quality)
        
    def enable_ambient_occlusion(self, enable=True):
        """Ambient occlusion etkinleştirir/devre dışı bırakır"""
        self._ambient_occlusion = enable
        return self
    
    def enable_motion_blur(self, enable=True):
        """Motion blur etkinleştirir/devre dışı bırakır"""
        self._motion_blur = enable
        return self
    
    def enable_depth_of_field(self, enable=True):
        """Depth of field etkinleştirir/devre dışı bırakır"""
        self._depth_of_field = enable
        return self
    
    def enable_anti_aliasing(self, enable=True):
        """Anti aliasing etkinleştirir/devre dışı bırakır"""
        self._anti_aliasing = enable
        return self
    
    def set_shadow_map_size(self, size):
        """Gölgeler için map boyutunu ayarlar"""
        self._shadow_map_size = max(256, min(8192, size))
        return self
    
    def set_reflection_quality(self, quality):
        """Yansıma kalitesini ayarlar"""
        self._reflection_quality = max(0.0, min(1.0, quality))
        return self
    
    def set_ao_samples(self, samples):
        """Ambient occlusion örneklem sayısını ayarlar"""
        self._ao_samples = max(1, min(64, samples))
        return self
    
    def set_blur_samples(self, samples):
        """Blur örneklem sayısını ayarlar"""
        self._blur_samples = max(1, min(32, samples))
        return self
    
    def set_depth_samples(self, samples):
        """Derinlik örneklem sayısını ayarlar"""
        self._depth_samples = max(1, min(16, samples))
        return self
    
    def set_render_quality(self, quality):
        """Render kalitesini ayarlar (0.0-1.0 arası)"""
        self._quality = max(0.0, min(1.0, quality))
        return self
    
    def enable_shadows(self, enable=True):
        """Gölgeleri etkinleştirir/devre dışı bırakır"""
        self._shadows = enable
        return self
    
    def enable_reflections(self, enable=True):
        """Yansımaları etkinleştirir/devre dışı bırakır"""
        self._reflections = enable
        return self
    
    def print_ren(self):
        """Render durumunu yazdırır"""
        print(f"Render durumu: {'Aktif' if self._rendering else 'Pasif'}")
        return self
    
    def print_fov(self):
        """Kamera görüş alanını yazdırır"""
        if self.camera is None:
            print("Kamera oluşturulmamış")
            return self
        print(f"Görüş alanı: {self.camera.fov} derece")
        return self
    
    def sins_entity(self, name):
        """Yeni entity oluşturur"""
        entity = Entity(name)
        if self.current_scene is not None:
            self.current_scene.objects.append(entity)
        return entity
    
    def ren_entity(self, name):
        """Entity'yi sahnede bulur"""
        if self.current_scene is None:
            raise ValueError("Aktif bir sahne yok")
        for obj in self.current_scene.objects:
            if isinstance(obj, Entity) and obj.name == name:
                return obj
        raise ValueError(f"Entity '{name}' bulunamadı")
    
    def load_ren_entity(self, name, scene_name=None):
        """Sahnedeki entity'yi yükler"""
        scene = self.scenes.get(scene_name) if scene_name else self.current_scene
        if scene is None:
            raise ValueError("Sahne bulunamadı")
            
        for obj in scene.objects:
            if isinstance(obj, Entity) and obj.name == name:
                return obj
        raise ValueError(f"Entity '{name}' bulunamadı")
    
    def polish(self, enable=True):
        """Render kalitesini ayarlar"""
        self._polish = enable
        return self
    
    def complete_ren(self):
        """Render işlemini tamamlar"""
        if not self._rendering:
            raise ValueError("Render işlemi aktif değil")
            
        self.render(self.current_scene)
        self.render_stop()
        return self
    
    def command_line(self, entity_name=None):
        """Hata durumunu kontrol eder"""
        if entity_name:
            entity = self.ren_entity(entity_name)
            entity.command_line()
        else:
            print("Genel sistem durumu:")
            print(f"Render durumu: {'Aktif' if self._rendering else 'Pasif'}")
            print(f"Aktif sahne: {self.current_scene.name if self.current_scene else 'Yok'}")
            print(f"Kamera durumu: {'Var' if self.camera else 'Yok'}")
        return self
    
    def point_entity(self, entity_name, scene_name=None):
        """Entity'i yok eder"""
        scene = self.scenes.get(scene_name) if scene_name else self.current_scene
        if scene is None:
            raise ValueError("Sahne bulunamadı")
            
        entity = None
        for obj in scene.objects:
            if isinstance(obj, Entity) and obj.name == entity_name:
                entity = obj
                break
        
        if entity is None:
            raise ValueError(f"Entity '{entity_name}' bulunamadı")
            
        entity.point_entity()
        return self
    
    def apply_force(self, entity_name, force, scene_name=None):
        """Entity'ye kuvvet uygular"""
        entity = self.ren_entity(entity_name)
        entity.physics.apply_force(np.array(force))
        return self
    
    def apply_torque(self, entity_name, torque, scene_name=None):
        """Entity'ye tork uygular"""
        entity = self.ren_entity(entity_name)
        entity.physics.apply_torque(np.array(torque))
        return self
    
    def update_physics(self, dt=0.016):
        """Fizik sistemini günceller"""
        if self.current_scene is None:
            return self
            
        for obj in self.current_scene.objects:
            if isinstance(obj, Entity):
                obj.physics.update(dt)
                obj.position = obj.physics.position
                obj.rotation = obj.physics.rotation
        return self
    
    def set_gravity(self, gravity):
        """Genel yer çekimi değerini ayarlar"""
        for obj in self.current_scene.objects:
            if isinstance(obj, Entity):
                obj.physics.gravity = np.array(gravity)
        return self
    
    def set_physics_properties(self, entity_name, mass=None, friction=None, restitution=None):
        """Entity fizik özelliklerini ayarlar"""
        entity = self.ren_entity(entity_name)
        if mass is not None:
            entity.physics.set_mass(mass)
        if friction is not None:
            entity.physics.friction = friction
        if restitution is not None:
            entity.physics.restitution = restitution
        return self
    
    def set_mass(self, mass, object_name):
        """Nesnenin kütlesini ayarlar"""
        entity = self.ren_entity(object_name)
        entity.physics.set_mass(mass)
        return self
    
    def fall(self, object_name, force):
        """Nesneyi düşürür"""
        entity = self.ren_entity(object_name)
        entity.physics.fall(force)
        return self
    
    def no_clip(self, object_name):
        """Nesneyi no-clip moduna alır"""
        entity = self.ren_entity(object_name)
        entity.physics.enable_no_clip(True)
        return self
    
    def unno_clip(self, object_name):
        """Nesneyi no-clip modundan çıkarır"""
        entity = self.ren_entity(object_name)
        entity.physics.enable_no_clip(False)
        return self
    
    def enable_physics(self, enable=True):
        """Fizik sistemini etkinleştirir/devre dışı bırakır"""
        if self.current_scene is None:
            return self
            
        for obj in self.current_scene.objects:
            if isinstance(obj, Entity):
                obj.physics.enable_physics(enable)
        return self
    
    def _render_object(self, obj, image):
        """Tek bir nesneyi render eder"""
        # Bu metod daha sonra detaylı implementasyon alacak
        pass

class Scene:
    def __init__(self):
        """Sahne sınıfı"""
        self.objects = []
        self.materials = {}
        self.position = np.array([0, 0, 0])
        self.scale = np.array([1, 1, 1])
        self.rotation = np.array([0, 0, 0])
        
    def add_object(self, obj_type, position=(0, 0, 0), scale=(1, 1, 1)):
        """Sahneye nesne ekler"""
        obj = Object(obj_type, position, scale)
        self.objects.append(obj)
        return obj

class Physics:
    def __init__(self):
        """Fizik özelliklerini yöneten sınıf"""
        # Temel fizik özellikleri
        self.mass = 1.0
        self.friction = 0.5
        self.restitution = 0.8
        self.drag = 0.01
        self.linear_damping = 0.99
        self.angular_damping = 0.99
        
        # Hareket durumu
        self.velocity = np.array([0, 0, 0])
        self.angular_velocity = np.array([0, 0, 0])
        self.position = np.array([0, 0, 0])
        self.rotation = np.array([0, 0, 0])
        self.acceleration = np.array([0, 0, 0])
        self.angular_acceleration = np.array([0, 0, 0])
        
        # Kuvvetler ve momentler
        self.gravity = np.array([0, -9.81, 0])
        self.forces = []
        self.torques = []
        self.force_accumulator = np.array([0, 0, 0])
        self.torque_accumulator = np.array([0, 0, 0])
        
        # Çarpışma ve raycast
        self.no_clip = False
        self.enabled = True
        self.collisions = []
        self.raycast = None
        self.raycast_distance = 100.0
        self.raycast_hit = None
        self.raycast_normal = None
        self.raycast_point = None
        self.raycast_object = None
        
        # Fizik durumu
        self.sleeping = False
        self.sleep_threshold = 0.01
        self.sleep_time = 0.0
        self.sleep_duration = 1.0
        
        # Fizik ayarları
        self.max_velocity = np.inf
        self.max_acceleration = np.inf
        self.max_angular_velocity = np.inf
        self.max_angular_acceleration = np.inf
        
        # Çarpışma tepkileri
        self.collision_response = True
        self.collision_group = 0
        self.collision_mask = 0xFFFFFFFF
        
        # Fizik materyali
        self.material = None
        
        # Fizik kısıtlamaları
        self.constraints = []
        self.joints = []
        
        # Fizik etkileşimleri
        self.contacts = []
        self.contact_forces = []
        
        # Fizik durumu
        self.state = {
            "position": self.position,
            "rotation": self.rotation,
            "velocity": self.velocity,
            "angular_velocity": self.angular_velocity
        }
        
        # Fizik hafızası
        self.history = []
        self.max_history = 100
        
        # Fizik istatistikleri
        self.stats = {
            "collisions": 0,
            "contacts": 0,
            "forces": 0,
            "torques": 0
        }
        
    def apply_force(self, force):
        """Kuvvet uygular"""
        if self.enabled:
            self.forces.append(np.array(force))
        return self
    
    def apply_torque(self, torque):
        """Tork uygular"""
        if self.enabled:
            self.torques.append(np.array(torque))
        return self
    
    def set_mass(self, mass):
        """Kütle değerini ayarlar"""
        self.mass = max(0.001, mass)  # Kütle en az 0.001 olacak
        return self
    
    def enable_physics(self, enable=True):
        """Fizik sistemini etkinleştirir/devre dışı bırakır"""
        self.enabled = enable
        return self
    
    def enable_no_clip(self, enable=True):
        """Nesnenin diğer nesnelerle çarpışmasını engeller"""
        self.no_clip = enable
        return self
    
    def fall(self, force):
        """Nesneyi düşürür"""
        if self.enabled:
            self.velocity += np.array(force) / self.mass
        return self
    
    def update(self, dt):
        """Fizik durumunu günceller"""
        if not self.enabled:
            return self
            
        # Hız limiti kontrolü
        velocity_magnitude = np.linalg.norm(self.velocity)
        if velocity_magnitude > self.max_velocity:
            self.velocity = (self.velocity / velocity_magnitude) * self.max_velocity
            
        # Açısal hız limiti kontrolü
        angular_velocity_magnitude = np.linalg.norm(self.angular_velocity)
        if angular_velocity_magnitude > self.max_angular_velocity:
            self.angular_velocity = (self.angular_velocity / angular_velocity_magnitude) * self.max_angular_velocity
            
        # Hava direnci hesapla
        drag_force = -self.velocity * np.linalg.norm(self.velocity) * self.drag
        
        # Kuvvetleri topla
        self.force_accumulator = np.zeros(3)
        for force in self.forces:
            self.force_accumulator += force
            self.stats["forces"] += 1
        self.forces.clear()
        
        # Torkları topla
        self.torque_accumulator = np.zeros(3)
        for torque in self.torques:
            self.torque_accumulator += torque
            self.stats["torques"] += 1
        self.torques.clear()
        
        # Hareket hesaplaması
        self.acceleration = (self.force_accumulator + self.gravity + drag_force) / self.mass
        self.velocity += self.acceleration * dt
        self.velocity *= self.linear_damping
        
        # Rotasyon hesaplaması
        self.angular_acceleration = self.torque_accumulator
        self.angular_velocity += self.angular_acceleration * dt
        self.angular_velocity *= self.angular_damping
        
        # Pozisyon güncelle
        self.position += self.velocity * dt
        
        # Rotasyon güncelle
        self.rotation += self.angular_velocity * dt
        
        # Sürükleme kuvveti
        if not self.no_clip:
            friction_force = -self.velocity * self.friction
            self.velocity += friction_force * dt
            
        # Çarpışma tespiti
        self.detect_collisions()
        
        # Fizik durumu kaydet
        self.state = {
            "position": self.position.copy(),
            "rotation": self.rotation.copy(),
            "velocity": self.velocity.copy(),
            "angular_velocity": self.angular_velocity.copy()
        }
        
        # Hafıza güncelle
        self.history.append(self.state)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        # İstatistikleri güncelle
        self.stats["collisions"] = len(self.collisions)
        self.stats["contacts"] = len(self.contacts)
        
        # Uyku kontrolü
        if np.linalg.norm(self.velocity) < self.sleep_threshold and \
           np.linalg.norm(self.angular_velocity) < self.sleep_threshold:
            self.sleep_time += dt
            if self.sleep_time >= self.sleep_duration:
                self.sleeping = True
        else:
            self.sleep_time = 0.0
            self.sleeping = False
            
        return self
    
    def add_constraint(self, constraint):
        """Yeni bir fizik kısıtlaması ekler"""
        self.constraints.append(constraint)
        return self
    
    def add_joint(self, joint):
        """Yeni bir fizik birleşimi ekler"""
        self.joints.append(joint)
        return self
    
    def set_material(self, material):
        """Fizik materyalini ayarlar"""
        self.material = material
        return self
    
    def set_collision_group(self, group):
        """Çarpışma grubunu ayarlar"""
        self.collision_group = group
        return self
    
    def set_collision_mask(self, mask):
        """Çarpışma maskesini ayarlar"""
        self.collision_mask = mask
        return self
    
    def set_sleep_threshold(self, threshold):
        """Uyku eşiğini ayarlar"""
        self.sleep_threshold = max(0.0, threshold)
        return self
    
    def set_sleep_duration(self, duration):
        """Uyku süresini ayarlar"""
        self.sleep_duration = max(0.0, duration)
        return self
    
    def get_state_history(self):
        """Fizik durumu geçmişini döndürür"""
        return self.history
    
    def get_physics_stats(self):
        """Fizik istatistiklerini döndürür"""
        return self.stats
    
    def detect_collisions(self):
        """Çarpışmaları tespit eder"""
        self.collisions.clear()
        # Bu metod daha sonra detaylı implementasyon alacak
        return self
    
    def raycast(self, origin, direction, distance=None):
        """Raycast işlemi yapar"""
        if distance is None:
            distance = self.raycast_distance
            
        self.raycast = {
            "origin": origin,
            "direction": direction,
            "distance": distance
        }
        
        # Raycast hesaplaması
        self.raycast_hit = None
        self.raycast_normal = None
        self.raycast_point = None
        self.raycast_object = None
        
        # Bu metod daha sonra detaylı implementasyon alacak
        return self
    
    def set_drag(self, drag):
        """Hava direncini ayarlar"""
        self.drag = max(0.0, drag)
        return self
    
    def set_damping(self, linear=None, angular=None):
        """Amortisman değerlerini ayarlar"""
        if linear is not None:
            self.linear_damping = max(0.0, min(1.0, linear))
        if angular is not None:
            self.angular_damping = max(0.0, min(1.0, angular))
        return self
    
    def get_collisions(self):
        """Çarpışma listesini döndürür"""
        return self.collisions
    
    def get_raycast_result(self):
        """Raycast sonucunu döndürür"""
        return {
            "hit": self.raycast_hit,
            "normal": self.raycast_normal,
            "point": self.raycast_point,
            "object": self.raycast_object
        }

class Entity:
    def __init__(self, name):
        """Entity sınıfı"""
        self.name = name
        self.position = np.array([0, 0, 0])
        self.rotation = np.array([0, 0, 0])
        self.scale = np.array([1, 1, 1])
        self.material = None
        self.children = []
        self.errors = []
        self.physics = Physics()
        
    def command_line(self):
        """Hata durumunu kontrol eder"""
        if self.errors:
            print(f"Entity '{self.name}' hataları:")
            for error in self.errors:
                print(f"- {error}")
        else:
            print(f"Entity '{self.name}' hata yok")
        return self
    
    def add_error(self, error):
        """Yeni hata ekler"""
        self.errors.append(error)
        return self
    
    def remove_error(self, error):
        """Belirtilen hatayı kaldırır"""
        if error in self.errors:
            self.errors.remove(error)
        return self
    
    def clear_errors(self):
        """Tüm hataları temizler"""
        self.errors.clear()
        return self
        
    def move(self, x, y, z):
        """Entity'yi hareket ettirir"""
        self.position += np.array([x, y, z])
        return self
    
    def rotate(self, x, y, z):
        """Entity'yi döndürür"""
        self.rotation += np.array([x, y, z])
        return self
    
    def scale(self, x, y, z):
        """Entity'yi ölçeklendirir"""
        self.scale = np.array([x, y, z])
        return self
    
    def add_child(self, child):
        """Çocuk entity ekler"""
        self.children.append(child)
        return self
    
    def point_entity(self):
        """Entity'i yok eder"""
        self.name = None
        self.position = None
        self.rotation = None
        self.scale = None
        self.material = None
        self.children = []
        self.errors = []
        return self

class Object(Entity):
    def __init__(self, obj_type, position, scale):
        """3B nesne sınıfı"""
        super().__init__(f"object_{obj_type}")
        self.type = obj_type
        self.position = np.array(position)
        self.scale = np.array(scale)
        self.material = None

class Camera:
    def __init__(self, position, look_at):
        """Kamera sınıfı"""
        self.position = np.array(position)
        self.look_at = np.array(look_at)
        self.fov = 75

class Light:
    def __init__(self, position, color):
        """Işık kaynağı sınıfı"""
        self.position = np.array(position)
        self.color = np.array(color)
        self.intensity = 1.0

# Örnek kullanım
if __name__ == "__main__":
    renderer = ManoRender()
    
    # Yeni sahne oluştur
    scene = renderer.scene_new("main_scene")
    
    # Kamera ayarları
    renderer.camera_new(0, 0, 10, 0, 0, 0)
    
    # Işık ekleyelim
    renderer.add_light(position=(0, 0, 10), color=(1, 1, 1))
    
    # Entity işlemleri
    entity = renderer.sins_entity("main_entity")
    entity.move(1, 2, 3).rotate(0, 45, 0).scale(2, 2, 2)
    
    # Fizik özellikleri ayarlama
    renderer.set_physics_properties("main_entity", mass=2.0, friction=0.3, restitution=0.6)
    
    # Kütle değerini ayarlama
    renderer.set_mass(1.5, "main_entity")
    
    # Nesneyi düşürme
    renderer.fall("main_entity", [0, -10, 0])
    
    # No-clip modunu etkinleştirme
    renderer.no_clip("main_entity")
    
    # No-clip modundan çıkarma
    renderer.unno_clip("main_entity")
    
    # Fizik sistemini etkinleştirme
    renderer.enable_physics(True)
    
    # Render kalitesini ayarlama
    renderer.set_render_quality(0.8)
    
    # Gölgeleri etkinleştirme
    renderer.enable_shadows(True)
    
    # Yansımaları etkinleştirme
    renderer.enable_reflections(True)
    
    # Ambient occlusion etkinleştirme
    renderer.enable_ambient_occlusion(True)
    
    # Motion blur etkinleştirme
    renderer.enable_motion_blur(True)
    
    # Depth of field etkinleştirme
    renderer.enable_depth_of_field(True)
    
    # Anti aliasing etkinleştirme
    renderer.enable_anti_aliasing(True)
    
    # Render parametrelerini ayarlama
    renderer.set_shadow_map_size(4096)
    renderer.set_reflection_quality(0.9)
    renderer.set_ao_samples(16)
    renderer.set_blur_samples(8)
    renderer.set_depth_samples(4)
    
    # Ses sistemini etkinleştir
    renderer.enable_audio(True)
    
    # Ses cihazını ayarla
    renderer.set_audio_device(0)
    
    # Ses kaynağı oluştur
    source_id = renderer.create_audio_source(
        position=(0, 0, 0),
        volume=0.8,
        pitch=1.0
    )
    
    # Ses dinleyicisi oluştur
    listener_id = renderer.create_audio_listener(
        position=(0, 0, 0),
        forward=(0, 0, -1),
        up=(0, 1, 0)
    )
    
    # Ses efektlerini etkinleştir
    renderer.enable_reverb(True)
    renderer.enable_compression(True)
    renderer.enable_equalizer(True)
    renderer.enable_spatialization(True)
    renderer.enable_doppler(True)
    renderer.enable_occlusion(True)
    
    # Ses parametrelerini ayarla
    renderer.set_audio_volume(0.8)
    renderer.set_audio_balance(0.0)
    renderer.set_audio_pitch(1.0)
    
    # Ses dosyasını oynat
    renderer.play_sound(
        source_id,
        file_path="sound.wav",
        loop=True
    )
    
    # Render işlemini başlat
    renderer.render_start()
    
    # Sahneyi render et
    renderer.render(
        scene,
        width=1920,
        height=1080,
        quality=0.8,
        shadows=True,
        reflections=True,
        ambient_occlusion=True,
        motion_blur=True,
        depth_of_field=True,
        anti_aliasing=True
    )
    
    # Render işlemini tamamla
    renderer.complete_ren()

    # Ses durdur
    renderer.stop_sound(source_id)

    # Texture testi
    try:
        # Texture'ı yükle
        renderer.get_texture("wood_texture", "wood.png")

        # Küp oluştur
        renderer.create_object(
            name="wood_cube",
            position=[0, 0, 0],
            rotation=[0, 0, 0],
            scale=[1, 1, 1],
            geometry="cube"
        )

        # Texture'ı uygula
        renderer.set_texture("wood_texture", "wood_cube")

        # Raycast işlemi
        renderer.raycast(
            origin=[0, 0, 0],
            direction=[0, 0, -1],
            distance=1000.0
        )

        # Fizik durumunu güncelle
        renderer.update_physics()
    except Exception as e:
        print(f"Texture testi sırasında hata oluştu: {str(e)}")

    # Raycast işlemi
    renderer.raycast(
        origin=[0, 0, 0],
        direction=[0, -1, 0],
        distance=100.0
    )

    # Raycast sonucunu al
    result = renderer.get_raycast_result()
    if result["hit"]:
        print(f"Raycast nesnesi: {result['object'].name}")
        print(f"Vuruş noktası: {result['point']}")
        print(f"Yüzey normali: {result['normal']}")

    # Entity'yi sahnede bul
    found_entity = renderer.ren_entity("main_entity")
    
    # Entity'yi yükle
    loaded_entity = renderer.load_ren_entity("main_entity", "main_scene")
    
    # Hata kontrolü
    entity.add_error("Test hatası")
    renderer.command_line("main_entity")
    entity.clear_errors()
    renderer.command_line("main_entity")
    
    # Genel sistem durumu
    renderer.command_line()
    
    # Entity'i yok et
    renderer.point_entity("main_entity")
    
    # Render kalitesini ayarla
    renderer.polish(True)
    
    # Render işlemini başlat
    renderer.render_start()
    
    # Sahneyi render et
    renderer.render(scene)
    
    # Render işlemini tamamla
    renderer.complete_ren()
