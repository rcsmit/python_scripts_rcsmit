import torch
from diffusers import FluxPipeline
import time


s1 = int(time.time())
pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload() #save some VRAM by offloading the model to CPU. Remove this if you have enough GPU power

prompt = "A cat holding a sign that says hello world"
image = pipe(
    prompt,
    guidance_scale=0.0,
    num_inference_steps=4,
    max_sequence_length=256,
    generator=torch.Generator("cpu").manual_seed(0)
).images[0]
image.save("flux-schnell.png")

s2 = int(time.time())
s2x = s2 - s1
print(" ")  # to compensate the  sys.stdout.flush()

print(f"Downloaded. Downloading  took {str(s2x)} seconds ....)")
