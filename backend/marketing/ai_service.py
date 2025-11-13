"""
AI Service for Content Generation - Using Free APIs
Supports: Hugging Face (free), OpenAI (free tier), and other free alternatives
"""
import requests
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class AIContentGenerator:
    """AI Content Generator using free APIs"""
    
    def __init__(self):
        # Hugging Face API (Free tier available)
        self.hf_api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        
        # Stability AI (Free tier available)
        self.stability_api_key = getattr(settings, 'STABILITY_API_KEY', None)
        self.stability_api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        # Replicate API (Free tier available)
        self.replicate_api_key = getattr(settings, 'REPLICATE_API_KEY', None)
        
        # OpenAI (Free tier available)
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        # Alternative: Use local models or other free services
        self.use_local = getattr(settings, 'USE_LOCAL_AI', False)
    
    def generate_text(self, prompt: str, max_length: int = 200, style: str = "professional", tone: str = "friendly") -> Dict:
        """
        Generate text content using AI
        """
        try:
            # Enhanced prompt with style and tone
            enhanced_prompt = f"Write a {style} and {tone} advertisement text: {prompt}"
            
            if self.openai_api_key:
                return self._generate_with_openai(enhanced_prompt, max_length)
            elif self.hf_api_key:
                return self._generate_with_huggingface(enhanced_prompt, max_length)
            else:
                # Fallback to template-based generation
                return self._generate_template_based(prompt, style, tone)
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return self._generate_template_based(prompt, style, tone)
    
    def _generate_with_openai(self, prompt: str, max_length: int) -> Dict:
        """Generate using OpenAI API"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Free tier model
                messages=[
                    {"role": "system", "content": "You are a creative marketing copywriter."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content
            return {
                'success': True,
                'text': generated_text,
                'model': 'gpt-3.5-turbo',
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return self._generate_template_based(prompt, "professional", "friendly")
    
    def _generate_with_huggingface(self, prompt: str, max_length: int) -> Dict:
        """Generate using Hugging Face API"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            model = "gpt2"  # Free model
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_length,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"{self.hf_api_url}/{model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result[0].get('generated_text', prompt)
                return {
                    'success': True,
                    'text': generated_text,
                    'model': 'gpt2-hf',
                    'tokens_used': len(generated_text.split())
                }
            else:
                logger.warning(f"Hugging Face API error: {response.status_code}")
                return self._generate_template_based(prompt, "professional", "friendly")
        except Exception as e:
            logger.error(f"Hugging Face generation error: {e}")
            return self._generate_template_based(prompt, "professional", "friendly")
    
    def _generate_template_based(self, prompt: str, style: str, tone: str) -> Dict:
        """Fallback template-based generation"""
        templates = {
            'professional': {
                'friendly': f"Discover {prompt}. Experience quality and excellence with us.",
                'formal': f"We are pleased to present {prompt}. Trusted by thousands.",
                'humorous': f"Looking for {prompt}? Look no further! We've got you covered."
            },
            'casual': {
                'friendly': f"Hey! Check out {prompt}. You're going to love it!",
                'formal': f"Introducing {prompt}. A perfect choice for you.",
                'humorous': f"{prompt}? Yes, please! Get yours today!"
            }
        }
        
        text = templates.get(style, templates['professional']).get(tone, templates['professional']['friendly'])
        return {
            'success': True,
            'text': text,
            'model': 'template-based',
            'tokens_used': 0
        }
    
    def generate_hashtags(self, content: str, count: int = 10) -> List[str]:
        """Generate relevant hashtags"""
        try:
            prompt = f"Generate {count} relevant hashtags for this content: {content}"
            result = self.generate_text(prompt, max_length=100)
            
            # Extract hashtags from text
            text = result.get('text', '')
            hashtags = []
            for word in text.split():
                if word.startswith('#'):
                    hashtags.append(word)
                elif len(hashtags) < count:
                    hashtags.append(f"#{word.replace('#', '').lower()}")
            
            # Fallback hashtags
            if len(hashtags) < 3:
                hashtags = ['#promotion', '#sale', '#offer', '#discount', '#new', '#trending', '#best', '#quality', '#affordable', '#limited']
            
            return hashtags[:count]
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            return ['#promotion', '#sale', '#offer', '#discount', '#new']
    
    def generate_headline(self, product_name: str = "", campaign_type: str = "product_promotion") -> str:
        """Generate catchy headline"""
        headlines = {
            'product_promotion': [
                f"Amazing {product_name} - Limited Time Offer!",
                f"Get Your {product_name} Today - Special Price!",
                f"{product_name} - Quality You Can Trust!",
            ],
            'seasonal_sale': [
                "Seasonal Sale - Up to 50% Off!",
                "Don't Miss Our Seasonal Specials!",
                "Seasonal Deals - Shop Now!",
            ],
            'new_product': [
                "Introducing Our Latest Innovation!",
                "New Arrival - Be the First to Experience!",
                "Something New is Here!",
            ],
            'brand_awareness': [
                "Your Trusted Partner Since Day One",
                "Quality. Service. Excellence.",
                "Building Relationships, One Customer at a Time",
            ]
        }
        
        import random
        options = headlines.get(campaign_type, headlines['product_promotion'])
        return random.choice(options)
    
    def generate_cta(self, campaign_type: str = "product_promotion") -> str:
        """Generate Call-to-Action"""
        ctas = {
            'product_promotion': ["Shop Now", "Buy Now", "Get Yours", "Order Today"],
            'seasonal_sale': ["Shop the Sale", "Grab the Deal", "Claim Offer"],
            'new_product': ["Learn More", "Explore Now", "Discover More"],
            'brand_awareness': ["Follow Us", "Join Us", "Connect With Us"],
        }
        
        import random
        options = ctas.get(campaign_type, ctas['product_promotion'])
        return random.choice(options)
    
    def generate_image_prompt(self, product_name: str = "", campaign_type: str = "product_promotion", style: str = "professional") -> str:
        """Generate prompt for image generation"""
        base_prompts = {
            'product_promotion': f"Professional product photography of {product_name}, clean background, modern lighting, high quality, commercial style",
            'seasonal_sale': f"Festive sale banner design, vibrant colors, discount text overlay, {style} style, eye-catching",
            'new_product': f"Modern product launch design, sleek and contemporary, {product_name} featured prominently, {style} aesthetic",
            'brand_awareness': f"Brand identity design, {style} and elegant, professional, trustworthy appearance",
        }
        
        prompt = base_prompts.get(campaign_type, base_prompts['product_promotion'])
        return prompt
    
    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> Dict:
        """
        Generate image using AI (using free services) - Try multiple services for best results
        """
        try:
            # Enhanced prompt for better poster generation
            enhanced_prompt = f"Professional marketing poster design: {prompt}, high quality, modern design, eye-catching, commercial advertisement style, clean layout, vibrant colors"
            
            # Try Stability AI first (best quality for posters)
            if self.stability_api_key:
                result = self._generate_image_stability(enhanced_prompt, width, height)
                if result.get('success'):
                    return result
            
            # Try Replicate API (good free tier)
            if self.replicate_api_key:
                result = self._generate_image_replicate(enhanced_prompt, width, height)
                if result.get('success'):
                    return result
            
            # Try Hugging Face with better models
            if self.hf_api_key:
                result = self._generate_image_huggingface(enhanced_prompt, width, height)
                if result.get('success'):
                    return result
            
            # Fallback to alternative method
            import random
            logger.warning("Using fallback poster generation - consider adding API keys for better quality")
            return self._generate_image_alternative(enhanced_prompt, width, height, style_variant=random.randint(0, 9))
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            import random
            return self._generate_image_alternative(prompt, width, height, style_variant=random.randint(0, 9))
    
    def _generate_image_stability(self, prompt: str, width: int, height: int) -> Dict:
        """Generate image using Stability AI (best quality for posters)"""
        try:
            import base64
            import io
            
            headers = {
                "Authorization": f"Bearer {self.stability_api_key}",
                "Accept": "image/*"
            }
            
            data = {
                "prompt": prompt,
                "output_format": "png",
                "mode": "text-to-image",
                "model": "sd3",
                "width": width,
                "height": height,
                "aspect_ratio": f"{width}:{height}",
            }
            
            response = requests.post(
                self.stability_api_url,
                headers=headers,
                files={"none": ""},
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'image_data': response.content,
                    'model': 'stability-ai-sd3',
                    'format': 'png'
                }
            else:
                logger.warning(f"Stability AI error: {response.status_code} - {response.text}")
                return {'success': False, 'message': f'Stability AI error: {response.status_code}'}
        except Exception as e:
            logger.error(f"Stability AI generation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def _generate_image_replicate(self, prompt: str, width: int, height: int) -> Dict:
        """Generate image using Replicate API (good free tier)"""
        try:
            import replicate
            import os
            os.environ['REPLICATE_API_TOKEN'] = self.replicate_api_key
            
            # Use a good free model for posters - Flux is excellent
            model = "black-forest-labs/flux-schnell"
            
            output = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                    "guidance_scale": 3.5,
                    "num_inference_steps": 4
                }
            )
            
            if output and len(output) > 0:
                image_url = output[0] if isinstance(output, list) else output
                image_response = requests.get(image_url, timeout=30)
                
                if image_response.status_code == 200:
                    return {
                        'success': True,
                        'image_data': image_response.content,
                        'model': 'replicate-flux-schnell',
                        'format': 'png'
                    }
            
            return {'success': False, 'message': 'Replicate API returned no image'}
        except Exception as e:
            logger.error(f"Replicate generation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def _generate_image_alternative(self, prompt: str, width: int, height: int, style_variant: int = 0) -> Dict:
        """Generate high-quality promotional poster using PIL/Pillow with different styles"""
        try:
            from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
            import io
            import random
            import math
            
            # Expanded style configurations with much more variety
            style_configs = [
                {
                    'name': 'Modern Minimalist',
                    'bg_type': 'gradient_vertical',
                    'bg_colors': [(240, 248, 255), (176, 196, 222)],
                    'text_color': (30, 30, 30),
                    'accent_color': (70, 130, 180),
                    'layout': 'centered',
                    'font_size': 72,
                    'has_shapes': False,
                    'has_pattern': False,
                    'border_style': 'thin',
                },
                {
                    'name': 'Vibrant Bold',
                    'bg_type': 'gradient_diagonal',
                    'bg_colors': [(255, 20, 147), (255, 165, 0)],
                    'text_color': (255, 255, 255),
                    'accent_color': (255, 255, 0),
                    'layout': 'offset',
                    'font_size': 80,
                    'has_shapes': True,
                    'has_pattern': True,
                    'border_style': 'thick',
                },
                {
                    'name': 'Elegant Premium',
                    'bg_type': 'solid_dark',
                    'bg_colors': [(20, 20, 30), (40, 40, 60)],
                    'text_color': (255, 215, 0),
                    'accent_color': (192, 192, 192),
                    'layout': 'centered',
                    'font_size': 68,
                    'has_shapes': True,
                    'has_pattern': False,
                    'border_style': 'elegant',
                },
                {
                    'name': 'Dynamic Energy',
                    'bg_type': 'gradient_radial',
                    'bg_colors': [(138, 43, 226), (30, 144, 255)],
                    'text_color': (255, 255, 255),
                    'accent_color': (255, 20, 147),
                    'layout': 'dynamic',
                    'font_size': 76,
                    'has_shapes': True,
                    'has_pattern': True,
                    'border_style': 'none',
                },
                {
                    'name': 'Classic Professional',
                    'bg_type': 'gradient_horizontal',
                    'bg_colors': [(245, 245, 245), (220, 220, 220)],
                    'text_color': (50, 50, 50),
                    'accent_color': (0, 100, 200),
                    'layout': 'centered',
                    'font_size': 70,
                    'has_shapes': False,
                    'has_pattern': False,
                    'border_style': 'thin',
                },
                {
                    'name': 'Bold Geometric',
                    'bg_type': 'geometric_pattern',
                    'bg_colors': [(255, 87, 34), (255, 152, 0)],
                    'text_color': (255, 255, 255),
                    'accent_color': (33, 33, 33),
                    'layout': 'geometric',
                    'font_size': 85,
                    'has_shapes': True,
                    'has_pattern': True,
                    'border_style': 'geometric',
                },
                {
                    'name': 'Nature Fresh',
                    'bg_type': 'gradient_vertical',
                    'bg_colors': [(76, 175, 80), (139, 195, 74)],
                    'text_color': (255, 255, 255),
                    'accent_color': (255, 193, 7),
                    'layout': 'nature',
                    'font_size': 74,
                    'has_shapes': True,
                    'has_pattern': False,
                    'border_style': 'organic',
                },
                {
                    'name': 'Tech Futuristic',
                    'bg_type': 'tech_pattern',
                    'bg_colors': [(0, 0, 0), (20, 20, 40)],
                    'text_color': (0, 255, 255),
                    'accent_color': (255, 0, 255),
                    'layout': 'tech',
                    'font_size': 78,
                    'has_shapes': True,
                    'has_pattern': True,
                    'border_style': 'glow',
                },
                {
                    'name': 'Luxury Gold',
                    'bg_type': 'gradient_radial',
                    'bg_colors': [(184, 134, 11), (139, 69, 19)],
                    'text_color': (255, 255, 255),
                    'accent_color': (255, 215, 0),
                    'layout': 'luxury',
                    'font_size': 82,
                    'has_shapes': True,
                    'has_pattern': True,
                    'border_style': 'luxury',
                },
                {
                    'name': 'Playful Colorful',
                    'bg_type': 'colorful_pattern',
                    'bg_colors': [(255, 0, 150), (0, 255, 255)],
                    'text_color': (255, 255, 255),
                    'accent_color': (255, 255, 0),
                    'layout': 'playful',
                    'font_size': 88,
                    'has_shapes': True,
                    'has_pattern': True,
                    'border_style': 'colorful',
                },
            ]
            
            # Select style based on variant with randomization
            base_config = style_configs[style_variant % len(style_configs)]
            config = base_config.copy()
            
            # Add randomization to make each poster unique
            seed_value = hash(prompt + str(style_variant)) % 10000
            random.seed(seed_value)
            
            # Randomize some config values for uniqueness
            config['font_size'] = int(config['font_size'] * random.uniform(0.9, 1.1))
            if random.random() > 0.5:
                # Sometimes swap colors
                config['bg_colors'] = list(reversed(config['bg_colors']))
            
            # Create image
            img = Image.new('RGB', (width, height), color=config['bg_colors'][0])
            draw = ImageDraw.Draw(img)
            
            # Draw background based on type
            if config['bg_type'] == 'gradient_vertical':
                for i in range(height):
                    ratio = i / height
                    r = int(config['bg_colors'][0][0] * (1 - ratio) + config['bg_colors'][1][0] * ratio)
                    g = int(config['bg_colors'][0][1] * (1 - ratio) + config['bg_colors'][1][1] * ratio)
                    b = int(config['bg_colors'][0][2] * (1 - ratio) + config['bg_colors'][1][2] * ratio)
                    draw.line([(0, i), (width, i)], fill=(r, g, b))
            elif config['bg_type'] == 'gradient_diagonal':
                # Optimized diagonal gradient
                max_dist = math.sqrt(width**2 + height**2)
                for y in range(0, height, 2):  # Step by 2 for performance
                    for x in range(0, width, 2):
                        dist = math.sqrt((x - 0)**2 + (y - 0)**2)
                        ratio = min(dist / max_dist, 1.0)
                        r = int(config['bg_colors'][0][0] * (1 - ratio) + config['bg_colors'][1][0] * ratio)
                        g = int(config['bg_colors'][0][1] * (1 - ratio) + config['bg_colors'][1][1] * ratio)
                        b = int(config['bg_colors'][0][2] * (1 - ratio) + config['bg_colors'][1][2] * ratio)
                        draw.rectangle([(x, y), (min(x+2, width), min(y+2, height))], fill=(r, g, b))
            elif config['bg_type'] == 'gradient_radial':
                center_x, center_y = width // 2, height // 2
                max_dist = math.sqrt(center_x**2 + center_y**2)
                # Optimize by using larger steps
                step = max(1, min(width, height) // 200)
                for y in range(0, height, step):
                    for x in range(0, width, step):
                        dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                        ratio = min(dist / max_dist, 1.0)
                        r = int(config['bg_colors'][0][0] * (1 - ratio) + config['bg_colors'][1][0] * ratio)
                        g = int(config['bg_colors'][0][1] * (1 - ratio) + config['bg_colors'][1][1] * ratio)
                        b = int(config['bg_colors'][0][2] * (1 - ratio) + config['bg_colors'][1][2] * ratio)
                        draw.rectangle([(x, y), (min(x+step, width), min(y+step, height))], fill=(r, g, b))
            elif config['bg_type'] == 'gradient_horizontal':
                for i in range(width):
                    ratio = i / width
                    r = int(config['bg_colors'][0][0] * (1 - ratio) + config['bg_colors'][1][0] * ratio)
                    g = int(config['bg_colors'][0][1] * (1 - ratio) + config['bg_colors'][1][1] * ratio)
                    b = int(config['bg_colors'][0][2] * (1 - ratio) + config['bg_colors'][1][2] * ratio)
                    draw.line([(i, 0), (i, height)], fill=(r, g, b))
            elif config['bg_type'] == 'solid_dark':
                draw.rectangle([(0, 0), (width, height)], fill=config['bg_colors'][0])
            elif config['bg_type'] == 'geometric_pattern':
                # Geometric pattern background
                draw.rectangle([(0, 0), (width, height)], fill=config['bg_colors'][0])
                pattern_size = 60
                for y in range(0, height, pattern_size):
                    for x in range(0, width, pattern_size):
                        if (x // pattern_size + y // pattern_size) % 2 == 0:
                            draw.rectangle([(x, y), (x+pattern_size, y+pattern_size)], 
                                         fill=config['bg_colors'][1])
                        # Add triangles
                        if random.random() > 0.7:
                            points = [(x, y), (x+pattern_size, y), (x+pattern_size//2, y+pattern_size)]
                            draw.polygon(points, outline=config['accent_color'], width=2)
            elif config['bg_type'] == 'tech_pattern':
                # Tech/futuristic pattern
                draw.rectangle([(0, 0), (width, height)], fill=config['bg_colors'][0])
                # Grid lines
                for i in range(0, width, 40):
                    draw.line([(i, 0), (i, height)], fill=(20, 20, 40), width=1)
                for i in range(0, height, 40):
                    draw.line([(0, i), (width, i)], fill=(20, 20, 40), width=1)
                # Add tech circles
                for _ in range(8):
                    x = random.randint(50, width-50)
                    y = random.randint(50, height-50)
                    radius = random.randint(30, 80)
                    draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               outline=config['accent_color'], width=2)
            elif config['bg_type'] == 'colorful_pattern':
                # Colorful pattern with multiple colors
                draw.rectangle([(0, 0), (width, height)], fill=config['bg_colors'][0])
                # Add colorful circles
                colors = [config['bg_colors'][1], config['accent_color'], 
                         (255, 100, 100), (100, 255, 100), (100, 100, 255)]
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                for _ in range(15):
                    x = random.randint(0, width)
                    y = random.randint(0, height)
                    radius = random.randint(20, 100)
                    color = random.choice(colors)
                    overlay_draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                                       fill=color + (100,))
                    draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               outline=color, width=2)
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
            
            # Add decorative shapes and patterns
            if config['has_shapes']:
                shape_count = random.randint(3, 8)
                for _ in range(shape_count):
                    shape_type = random.choice(['circle', 'rectangle', 'line', 'triangle', 'polygon'])
                    x = random.randint(0, width)
                    y = random.randint(0, height)
                    
                    if shape_type == 'circle':
                        radius = random.randint(30, 150)
                        if random.random() > 0.5:
                            # Semi-transparent fill - create overlay
                            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                            overlay_draw = ImageDraw.Draw(overlay)
                            overlay_draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                                               fill=config['accent_color'] + (128,))
                            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                            draw = ImageDraw.Draw(img)
                        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                                   outline=config['accent_color'], width=3)
                    elif shape_type == 'rectangle':
                        w = random.randint(50, 200)
                        h = random.randint(50, 200)
                        if random.random() > 0.5:
                            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                            overlay_draw = ImageDraw.Draw(overlay)
                            overlay_draw.rectangle([x, y, x+w, y+h], 
                                                  fill=config['accent_color'] + (76,))
                            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                            draw = ImageDraw.Draw(img)
                        draw.rectangle([x, y, x+w, y+h], 
                                     outline=config['accent_color'], width=2)
                    elif shape_type == 'line':
                        x2 = random.randint(0, width)
                        y2 = random.randint(0, height)
                        draw.line([(x, y), (x2, y2)], fill=config['accent_color'], width=random.randint(2, 5))
                    elif shape_type == 'triangle':
                        size = random.randint(40, 120)
                        points = [(x, y), (x+size, y), (x+size//2, y+size)]
                        draw.polygon(points, outline=config['accent_color'], width=3)
            
            # Add patterns if needed
            if config['has_pattern']:
                pattern_type = random.choice(['dots', 'stripes', 'waves', 'diagonal'])
                if pattern_type == 'dots':
                    for dot_y in range(0, height, 30):
                        for dot_x in range(0, width, 30):
                            if random.random() > 0.7:
                                draw.ellipse([dot_x-3, dot_y-3, dot_x+3, dot_y+3], fill=config['accent_color'])
                elif pattern_type == 'stripes':
                    stripe_width = 20
                    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    for i in range(0, width, stripe_width * 2):
                        overlay_draw.rectangle([(i, 0), (i+stripe_width, height)], 
                                             fill=config['accent_color'] + (76,))
                    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                    draw = ImageDraw.Draw(img)
                elif pattern_type == 'waves':
                    for wave_y in range(0, height, 40):
                        wave_points = []
                        for wave_x in range(0, width, 10):
                            wave_y_offset = wave_y + int(20 * math.sin(wave_x / 20))
                            wave_points.append((wave_x, wave_y_offset))
                        if len(wave_points) > 1:
                            for i in range(len(wave_points) - 1):
                                draw.line([wave_points[i], wave_points[i+1]], 
                                        fill=config['accent_color'], width=2)
            
            # Prepare text
            words = prompt.split()[:12]
            headline = ' '.join(words[:6])
            subline = ' '.join(words[6:]) if len(words) > 6 else ''
            
            # Try to load fonts
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", config['font_size'])
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", config['font_size'] // 2)
            except:
                try:
                    font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", config['font_size'])
                    font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", config['font_size'] // 2)
                except:
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
            
            # Draw text based on layout with much more variety
            bbox = draw.textbbox((0, 0), headline, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if config['layout'] == 'centered':
                x = (width - text_width) // 2
                y = (height - text_height) // 2 - (text_height if subline else 0)
                # Text shadow with multiple layers for depth
                for offset in [(5, 5), (3, 3)]:
                    draw.text((x + offset[0], y + offset[1]), headline, fill=(0, 0, 0, 100), font=font_large)
                draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    bbox2 = draw.textbbox((0, 0), subline, font=font_medium)
                    text_width2 = bbox2[2] - bbox2[0]
                    x2 = (width - text_width2) // 2
                    y2 = y + text_height + 25
                    draw.text((x2 + 2, y2 + 2), subline, fill=(0, 0, 0, 100), font=font_medium)
                    draw.text((x2, y2), subline, fill=config['accent_color'], font=font_medium)
                    
            elif config['layout'] == 'offset':
                x = width // 10
                y = height // 4
                # Bold shadow
                for offset in [(6, 6), (3, 3)]:
                    draw.text((x + offset[0], y + offset[1]), headline, fill=(0, 0, 0, 150), font=font_large)
                draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    y2 = y + int(text_height * 1.4)
                    draw.text((x + 3, y2 + 3), subline, fill=(0, 0, 0, 150), font=font_medium)
                    draw.text((x, y2), subline, fill=config['accent_color'], font=font_medium)
                    
            elif config['layout'] == 'dynamic':
                angle = random.choice([-8, -5, 5, 8])
                x = width // 8
                y = height // 5
                
                text_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)
                text_draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                rotated = text_img.rotate(angle, expand=False)
                img.paste(rotated, (0, 0), rotated)
                
                if subline:
                    text_img2 = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                    text_draw2 = ImageDraw.Draw(text_img2)
                    y2 = y + int(text_height * 1.3)
                    text_draw2.text((x, y2), subline, fill=config['accent_color'], font=font_medium)
                    rotated2 = text_img2.rotate(-angle, expand=False)
                    img.paste(rotated2, (0, 0), rotated2)
                    
            elif config['layout'] == 'geometric':
                # Geometric layout with boxes around text
                x = width // 6
                y = height // 3
                # Draw geometric box behind text
                box_padding = 20
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([(x - box_padding, y - box_padding), 
                                       (x + text_width + box_padding, y + text_height + box_padding)],
                                      fill=config['accent_color'] + (180,))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                draw.rectangle([(x - box_padding, y - box_padding), 
                              (x + text_width + box_padding, y + text_height + box_padding)],
                             outline=config['text_color'], width=4)
                draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    y2 = y + text_height + 40
                    draw.rectangle([(x - box_padding//2, y2 - box_padding//2),
                                  (x + text_width + box_padding//2, y2 + text_height//2 + box_padding//2)],
                                 outline=config['accent_color'], width=3)
                    draw.text((x, y2), subline, fill=config['accent_color'], font=font_medium)
                    
            elif config['layout'] == 'nature':
                # Organic, flowing layout
                x = width // 8
                y = height // 3
                # Add organic shapes around text
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                for i in range(3):
                    offset_x = random.randint(-30, 30)
                    offset_y = random.randint(-30, 30)
                    radius = random.randint(20, 50)
                    overlay_draw.ellipse([x + offset_x - radius, y + offset_y - radius,
                                         x + offset_x + radius, y + offset_y + radius],
                                        fill=config['accent_color'] + (80,))
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                
                draw.text((x + 4, y + 4), headline, fill=(0, 0, 0, 120), font=font_large)
                draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    y2 = y + int(text_height * 1.5)
                    draw.text((x, y2), subline, fill=config['accent_color'], font=font_medium)
                    
            elif config['layout'] == 'tech':
                # Tech/futuristic layout with lines
                x = width // 10
                y = height // 4
                # Add tech lines
                draw.line([(x - 20, y), (x - 5, y)], fill=config['accent_color'], width=3)
                draw.line([(x + text_width + 5, y), (x + text_width + 20, y)], fill=config['accent_color'], width=3)
                draw.line([(x - 20, y + text_height), (x - 5, y + text_height)], fill=config['accent_color'], width=3)
                draw.line([(x + text_width + 5, y + text_height), (x + text_width + 20, y + text_height)], fill=config['accent_color'], width=3)
                
                # Glow effect
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                for glow_offset in range(1, 4):
                    glow_color = tuple(min(255, c + glow_offset * 20) for c in config['text_color'])
                    overlay_draw.text((x - glow_offset, y - glow_offset), headline, 
                                    fill=glow_color + (100,), font=font_large)
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    y2 = y + int(text_height * 1.4)
                    draw.text((x, y2), subline, fill=config['accent_color'], font=font_medium)
                    
            elif config['layout'] == 'luxury':
                # Luxury layout with elegant framing
                x = (width - text_width) // 2
                y = (height - text_height) // 2 - (text_height if subline else 0)
                # Add luxury frame
                frame_width = 8
                draw.rectangle([(x - 40, y - 40), (x + text_width + 40, y + text_height + 40)],
                             outline=config['accent_color'], width=frame_width)
                draw.rectangle([(x - 30, y - 30), (x + text_width + 30, y + text_height + 30)],
                             outline=config['text_color'], width=2)
                
                # Gold text with shadow
                draw.text((x + 4, y + 4), headline, fill=(0, 0, 0, 150), font=font_large)
                draw.text((x, y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    bbox2 = draw.textbbox((0, 0), subline, font=font_medium)
                    text_width2 = bbox2[2] - bbox2[0]
                    x2 = (width - text_width2) // 2
                    y2 = y + text_height + 30
                    draw.text((x2, y2), subline, fill=config['accent_color'], font=font_medium)
                    
            elif config['layout'] == 'playful':
                # Playful, scattered layout
                x = width // 7
                y = height // 5
                # Multiple text positions for playful effect
                positions = [(x, y), (x + 20, y + 10), (x + 10, y + 5)]
                for pos_x, pos_y in positions[:1]:  # Use first position for main text
                    draw.text((pos_x + 3, pos_y + 3), headline, fill=(0, 0, 0, 120), font=font_large)
                    draw.text((pos_x, pos_y), headline, fill=config['text_color'], font=font_large)
                
                if subline:
                    y2 = y + int(text_height * 1.6)
                    x2 = x + random.randint(-10, 10)
                    draw.text((x2, y2), subline, fill=config['accent_color'], font=font_medium)
            
            # Add borders based on style
            if config['border_style'] == 'thin':
                draw.rectangle([(0, 0), (width-1, height-1)], outline=config['accent_color'], width=3)
            elif config['border_style'] == 'thick':
                for i in range(3):
                    draw.rectangle([(i, i), (width-1-i, height-1-i)], outline=config['accent_color'], width=2)
            elif config['border_style'] == 'elegant':
                # Double border
                draw.rectangle([(0, 0), (width-1, height-1)], outline=config['accent_color'], width=4)
                draw.rectangle([(10, 10), (width-11, height-11)], outline=config['text_color'], width=2)
            elif config['border_style'] == 'geometric':
                # Dashed border effect
                dash_length = 20
                for i in range(0, width, dash_length * 2):
                    draw.line([(i, 0), (i + dash_length, 0)], fill=config['accent_color'], width=5)
                    draw.line([(i, height-1), (i + dash_length, height-1)], fill=config['accent_color'], width=5)
                for i in range(0, height, dash_length * 2):
                    draw.line([(0, i), (0, i + dash_length)], fill=config['accent_color'], width=5)
                    draw.line([(width-1, i), (width-1, i + dash_length)], fill=config['accent_color'], width=5)
            elif config['border_style'] == 'organic':
                # Wavy border
                for x in range(0, width, 5):
                    y_offset = int(10 * math.sin(x / 30))
                    draw.ellipse([(x-2, y_offset-2), (x+2, y_offset+2)], fill=config['accent_color'])
                    draw.ellipse([(x-2, height-1-y_offset-2), (x+2, height-1-y_offset+2)], fill=config['accent_color'])
            elif config['border_style'] == 'glow':
                # Glowing border effect
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                for i in range(5):
                    alpha = 200 - i * 40
                    color = tuple(min(255, c + i * 10) for c in config['accent_color'])
                    overlay_draw.rectangle([(i, i), (width-1-i, height-1-i)], 
                                          outline=color + (alpha,), width=1)
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
            elif config['border_style'] == 'luxury':
                # Ornate border
                draw.rectangle([(0, 0), (width-1, height-1)], outline=config['accent_color'], width=6)
                # Add corner decorations
                corner_size = 30
                for corner_x, corner_y in [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]:
                    if corner_x == 0 and corner_y == 0:
                        draw.arc([corner_x, corner_y, corner_x + corner_size*2, corner_y + corner_size*2], 
                                start=0, end=90, fill=config['accent_color'], width=4)
                    elif corner_x == width-1 and corner_y == 0:
                        draw.arc([corner_x - corner_size*2, corner_y, corner_x, corner_y + corner_size*2],
                                start=90, end=180, fill=config['accent_color'], width=4)
                    elif corner_x == 0 and corner_y == height-1:
                        draw.arc([corner_x, corner_y - corner_size*2, corner_x + corner_size*2, corner_y],
                                start=270, end=360, fill=config['accent_color'], width=4)
                    else:
                        draw.arc([corner_x - corner_size*2, corner_y - corner_size*2, corner_x, corner_y],
                                start=180, end=270, fill=config['accent_color'], width=4)
            elif config['border_style'] == 'colorful':
                # Multi-color border
                colors = [config['accent_color'], config['bg_colors'][1], (255, 100, 100)]
                for i, color in enumerate(colors):
                    draw.rectangle([(i*3, i*3), (width-1-i*3, height-1-i*3)], outline=color, width=2)
            
            # Apply post-processing effects
            if config['name'] == 'Elegant Premium':
                img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            elif config['name'] == 'Tech Futuristic':
                # Add slight sharpening
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.2)
            
            # Save to bytes
            img_io = io.BytesIO()
            img.save(img_io, format='PNG', quality=95, optimize=True)
            img_io.seek(0)
            
            return {
                'success': True,
                'image_data': img_io.getvalue(),
                'model': f'pillow-{config["name"].lower().replace(" ", "-")}',
                'format': 'png',
                'style': config['name']
            }
        except Exception as e:
            logger.error(f"Alternative image generation error: {e}")
            return {
                'success': False,
                'message': 'Image generation failed. Please upload an image manually.',
                'placeholder': True
            }
    
    def _generate_image_huggingface(self, prompt: str, width: int, height: int) -> Dict:
        """Generate image using Hugging Face Stable Diffusion with better models"""
        try:
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            # Try better models first, fallback to free ones
            models = [
                "stabilityai/stable-diffusion-xl-base-1.0",  # Better quality
                "runwayml/stable-diffusion-v1-5",  # Good quality
                "stabilityai/stable-diffusion-2-1",  # Free tier
            ]
            
            for model in models:
                try:
                    response = requests.post(
                        f"{self.hf_api_url}/{model}",
                        headers=headers,
                        json={
                            "inputs": prompt,
                            "parameters": {
                                "width": width,
                                "height": height,
                                "num_inference_steps": 30,
                                "guidance_scale": 7.5
                            }
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'image_data': response.content,
                            'model': model,
                            'format': 'png'
                        }
                    elif response.status_code == 503:
                        # Model is loading, wait and retry
                        import time
                        time.sleep(5)
                        continue
                except Exception as e:
                    logger.warning(f"HF model {model} failed: {e}")
                    continue
            
            return {'success': False, 'message': 'All Hugging Face models failed'}
        except Exception as e:
            logger.error(f"Hugging Face image generation error: {e}")
            return {
                'success': False,
                'message': str(e),
                'placeholder': True
            }
    
    def generate_video_script(self, content: str, duration: int = 30) -> Dict:
        """Generate video script"""
        prompt = f"Create a {duration}-second video script for: {content}. Include scenes, narration, and visual descriptions."
        result = self.generate_text(prompt, max_length=500)
        
        # Parse script into scenes
        script_text = result.get('text', '')
        scenes = script_text.split('\n\n') if '\n\n' in script_text else [script_text]
        
        return {
            'success': True,
            'script': script_text,
            'scenes': scenes,
            'duration': duration
        }
    
    def generate_video(self, prompt: str, duration: int = 15, width: int = 1280, height: int = 720) -> Dict:
        """
        Generate video using AI or create a simple video from images
        """
        try:
            # For now, create a simple video from generated images
            # In production, you could use services like RunwayML, Pika, or Stable Video Diffusion
            return self._generate_video_from_images(prompt, duration, width, height)
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {
                'success': False,
                'message': f'Video generation failed: {str(e)}. Please upload a video manually.',
                'placeholder': True
            }
    
    def _generate_video_from_images(self, prompt: str, duration: int, width: int, height: int) -> Dict:
        """Create a simple video from generated images"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            import imageio
            import numpy as np
            
            # Generate multiple frames (images) for the video
            frames = []
            num_frames = min(duration * 2, 60)  # 2 fps, max 60 frames
            
            for i in range(num_frames):
                # Create frame with slight variations
                img = Image.new('RGB', (width, height), color='#FFFFFF')
                draw = ImageDraw.Draw(img)
                
                # Animated gradient
                progress = i / num_frames
                r = int(255 - progress * 100)
                g = int(200 - progress * 50)
                b = int(255 - progress * 30)
                
                for y in range(height):
                    color_factor = y / height
                    frame_r = int(r - color_factor * 50)
                    frame_g = int(g - color_factor * 30)
                    frame_b = int(b - color_factor * 20)
                    draw.line([(0, y), (width, y)], fill=(frame_r, frame_g, frame_b))
                
                # Add text
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                except:
                    font = ImageFont.load_default()
                
                words = prompt.split()[:8]
                text = ' '.join(words)
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((width - text_width) // 2, (height - text_height) // 2)
                
                # Animate text position
                y_offset = int(10 * np.sin(progress * 2 * np.pi))
                draw.text((position[0] + 2, position[1] + y_offset + 2), text, fill='#000000', font=font)
                draw.text((position[0], position[1] + y_offset), text, fill='#FFFFFF', font=font)
                
                # Convert to numpy array for imageio
                frames.append(np.array(img))
            
            # Create video
            video_io = io.BytesIO()
            try:
                # Try with codec first
                imageio.mimsave(video_io, frames, format='mp4', fps=2, codec='libx264', quality=5)
            except Exception as codec_error:
                # Fallback without codec specification
                try:
                    video_io = io.BytesIO()
                    imageio.mimsave(video_io, frames, format='mp4', fps=2)
                except Exception as e2:
                    logger.error(f"Video encoding error: {e2}")
                    raise e2
            video_io.seek(0)
            
            return {
                'success': True,
                'video_data': video_io.getvalue(),
                'model': 'imageio-generated',
                'format': 'mp4',
                'duration': duration
            }
        except ImportError:
            logger.warning("imageio not installed, cannot generate video")
            return {
                'success': False,
                'message': 'Video generation requires imageio library. Install with: pip install imageio imageio-ffmpeg',
                'placeholder': True
            }
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return {
                'success': False,
                'message': f'Video generation failed: {str(e)}',
                'placeholder': True
            }
    
    def generate_multiple_posters(self, base_prompt: str, count: int = 3, width: int = 1024, height: int = 1024, style: str = "professional") -> List[Dict]:
        """
        Generate multiple poster variations automatically with different styles
        """
        variations = []
        
        # Create unique prompt variations for each poster
        prompt_variations = [
            f"{base_prompt}",
            f"{base_prompt} - Premium Quality",
            f"{base_prompt} - Special Offer",
            f"{base_prompt} - Limited Edition",
            f"{base_prompt} - New Arrival",
            f"{base_prompt} - Best Deal",
            f"{base_prompt} - Exclusive",
            f"{base_prompt} - Trendy",
            f"{base_prompt} - Must Have",
            f"{base_prompt} - Top Choice",
        ]
        
        for i in range(count):
            try:
                variation_prompt = prompt_variations[i % len(prompt_variations)]
                
                # Try AI generation first
                result = self.generate_image(variation_prompt, width, height)
                
                # If AI fails or not available, use alternative with style variant
                if not result.get('success'):
                    result = self._generate_image_alternative(variation_prompt, width, height, style_variant=i)
                
                if result.get('success') and result.get('image_data'):
                    variations.append({
                        'index': i + 1,
                        'prompt': variation_prompt,
                        'image_data': result.get('image_data'),
                        'format': result.get('format', 'png'),
                        'style': result.get('style', f'Style {i+1}'),
                        'success': True
                    })
                else:
                    # Final fallback - ensure we always generate something
                    result = self._generate_image_alternative(variation_prompt, width, height, style_variant=i)
                    if result.get('success'):
                        variations.append({
                            'index': i + 1,
                            'prompt': variation_prompt,
                            'image_data': result.get('image_data'),
                            'format': result.get('format', 'png'),
                            'style': result.get('style', f'Style {i+1}'),
                            'success': True
                        })
            except Exception as e:
                logger.error(f"Error generating poster variation {i+1}: {e}")
                # Still try to generate a basic one
                try:
                    result = self._generate_image_alternative(base_prompt, width, height, style_variant=i)
                    if result.get('success'):
                        variations.append({
                            'index': i + 1,
                            'prompt': base_prompt,
                            'image_data': result.get('image_data'),
                            'format': result.get('format', 'png'),
                            'style': result.get('style', f'Style {i+1}'),
                            'success': True
                        })
                except:
                    continue
        
        return variations
    
    def analyze_audience(self, product_name: str = "", campaign_type: str = "product_promotion") -> Dict:
        """Analyze and suggest target audience"""
        prompt = f"Analyze target audience for {campaign_type} campaign featuring {product_name}. Suggest age range, interests, and demographics."
        result = self.generate_text(prompt, max_length=300)
        
        return {
            'success': True,
            'analysis': result.get('text', ''),
            'suggested_age_min': 18,
            'suggested_age_max': 65,
            'suggested_interests': ['shopping', 'lifestyle', 'quality products']
        }


# Singleton instance
ai_generator = AIContentGenerator()

