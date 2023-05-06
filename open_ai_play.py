from keys import * # secret file with the prices
import os
import openai
import requests
import shutil
import datetime

openai.api_key = OPENAI_API_KEY



# Remember that the model predicts which text is most likely to follow the text preceding it. 
# Temperature is a value between 0 and 1 that essentially lets you control how confident the
#  model should be when making these predictions. Lowering temperature means it will take fewer
#  risks, and completions will be more accurate and deterministic. Increasing temperature will
#  result in more diverse completions.

def create_cat():
    


    response = openai.Image.create(
    prompt="a white siamese cat",
    n=1,
    size="1024x1024"
    )
    img_url = response['data'][0]['url']
    print (img_url)
    
    # Download the image
    response = requests.get(img_url, stream=True)
    current_date_time = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    output_filename = f'generated_{current_date_time}.png'
    # Save it to a file
    with open(output_filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
        print (f"saved - {output_filename}")
    # Clean up
    del response


def index(animal):
        prompt = generate_prompt(animal)
        print (prompt)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.6,
        )
        return response.choices[0].text

   


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.
    Animal: {}
    Names:""".format(
            animal.capitalize()
        )
answer = index("cat")
print (answer)
#create_cat()
