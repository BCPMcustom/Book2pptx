import os
from pptx import Presentation
from pptx.util import Inches, Pt



class PowerPointRenderer:
    def render(self, presentation_spec):
        prs = Presentation("renderer/templates/Template.pptx")
        title_slide_layout = prs.slide_layouts[0]          #This layout used to give the title_bar located of title_slide
        slide_layout = prs.slide_layouts[0]                #This layout used to give title_bar at the top, and a multimedia box
        slide = prs.slides[0]   
        title = slide.shapes.title
        title.text = presentation_spec.title

        raw_path = ""
        img_path = ""
        i = -1
        
        for slide in presentation_spec.slides:
            callout_count = -1
            i += 1
            slide = prs.slides.add_slide(slide_layout)    
            title = slide.shapes.title
            title.text = presentation_spec.slides[i].title
            body_shape = slide.shapes.placeholders[0]
            


            for callout in presentation_spec.slides[i].callouts:
                callout_count += 1  
                callout = presentation_spec.slides[i].callouts[callout_count]
              
                if callout_count == 0:   
                    title = slide.shapes.title
                    title.text = presentation_spec.slides[i].title
                    continue
             
                elif callout_count > 1:
                    slide = prs.slides.add_slide(slide_layout)   
                    title = slide.shapes.title
                    title.text = presentation_spec.slides[i].title
                    continue


            if presentation_spec.slides[i].bullets:
                bullet_count = 0
                bullet = presentation_spec.slides[i].bullets
                for bullet[bullet_count] in presentation_spec.slides[i].bullets:
                    tf = body_shape.text_frame
                    p = tf.add_paragraph()
                    p.text = presentation_spec.slides[i].bullets[bullet_count]
                    p.font.size = Pt(22)



            if presentation_spec.slides[i].images:

                img_count = 0
                image = presentation_spec.slides[i].images

                for image[img_count] in presentation_spec.slides[i].images:
                            
                    raw_path = presentation_spec.slides[i].images[img_count]
                    img_path = os.path.abspath(raw_path)         
                    left = top = Inches(1)
                    pic = slide.shapes.add_picture(img_path, left, top)
                    img_count += 1


        slide = prs.slides.add_slide(title_slide_layout)    
        title = slide.shapes.title
        title.text = presentation_spec.closing_title

        return prs

        
