import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_FILL
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN



class PowerPointRenderer:

    def __init__(self):
        super().__init__()
        self.template = "renderer/templates/Template.pptx"
        self.block_fill = RGBColor(155, 155, 155)
        self.text_fill = RGBColor(255, 255, 255)
        self.left = Inches(0.7)
        self.block_width = Inches(8.6)     ###USES (9.6) with template, (8.6) without template
        self.ttlFontSize = Pt(42)
        self.ttlTop = Inches(0.75)
        self.ttlHeight = Inches(1.5)
        self.bodyTop = Inches(2.5)
        self.bodyHeight = Inches(4.5)
        self.closingTop = Inches(0.9)
        self.closingHeight = Inches(5.5)

        self.i = -1
        self.IStemplate = 0


    def render_titleBlock(self, slide):
        shapes = slide.shapes

        titleBar = shapes.add_shape(MSO_SHAPE.RECTANGLE, 
                                self.left, self.ttlTop, self.block_width, self.ttlHeight)        
        fill = titleBar.fill
        fill.solid()
        fill.fore_color.rgb = self.block_fill

        line = titleBar.line
        line.color.rgb = self.block_fill
        line.color.brightness = -0.15 # 15% darker
        line.width = Pt(2.5)

 

    def render_title(self, slide, title):
        shapes = slide.shapes

        txBoxTitle = slide.shapes.add_textbox(self.left, self.ttlTop, self.block_width, self.ttlHeight)
        tf = txBoxTitle.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()

        font = run.font
        font.size = self.ttlFontSize
        font.color.rgb = self.text_fill

        run.text = title 


    def render_bodyBlock(self, slide):
        shapes = slide.shapes

        bodyBlock = shapes.add_shape(MSO_SHAPE.RECTANGLE,   
                                self.left, self.bodyTop, self.block_width, self.bodyHeight)        
        fill = bodyBlock.fill
        fill.solid()
        fill.fore_color.rgb = self.block_fill

        line = bodyBlock.line
        line.color.rgb = self.block_fill
        line.color.brightness = -0.15 # 15% darker
        line.width = Pt(2.5)


    def render_closingBlock(self, slide):
        shapes = slide.shapes

        bodyBlock = shapes.add_shape(MSO_SHAPE.RECTANGLE,  
                                self.left, self.closingTop, self.block_width, self.closingHeight)        
        fill = bodyBlock.fill
        fill.solid()
        fill.fore_color.rgb = self.block_fill

        line = bodyBlock.line
        line.color.rgb = self.block_fill
        line.color.brightness = -0.15 # 15% darker
        line.width = Pt(2.5)



    def render_closing(self, slide, title):
        shapes = slide.shapes

        txBoxTitle = slide.shapes.add_textbox(self.left, self.closingTop, self.block_width, self.closingHeight)
        tf = txBoxTitle.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()

        font = run.font
        font.size = self.ttlFontSize
        font.color.rgb = self.text_fill

        run.text = title




    def render_bullets(self, slide, slide_spec):

        if slide_spec[self.i].bullets:

            shape = slide.shapes

            bullet_count = 0    
            bulletBlock = shape.add_textbox(self.left, self.bodyTop, self.block_width, self.bodyHeight)
            tf = bulletBlock.text_frame
            tf.word_wrap = True

            for bullet in slide_spec[self.i].bullets:

                if bullet_count == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                   
                p.alignment = PP_ALIGN.LEFT
                run = p.add_run()
        
                font = run.font
                font.size = Pt(22)
                font.color.rgb = self.text_fill

                run.text = "- " + bullet + "\n"
           
                if len(slide_spec[self.i].bullets) > 1:
                    bullet_count += 1

            bullet_count = 0




    def render_callouts(self, slide, slide_spec):

        if slide_spec[self.i].callouts:  

            text = slide_spec[self.i].callouts[0]

            shapes = slide.shapes 
            callout = slide.shapes.add_textbox(self.left, self.bodyTop, self.block_width, self.bodyHeight)
            tf = callout.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()

            font = run.font
            font.size = Pt(22)
            font.color.rgb = self.text_fill

            run.text = text 

          




    def render_images(self, slide, slide_spec):

        img_count = 0
        shape = slide.shapes

        for image in slide_spec[self.i].images:
            stagger = 1
            img_path = os.path.abspath(slide_spec[self.i].images[img_count])
            pic = slide.shapes.add_picture(img_path, Inches(stagger), Inches(stagger))
            img_count += 1
            stagger += 0.5




    def render(self, presentation_spec, IStemplate):   ###REFACTOR TO notUSE TEMPATE IN PROGRESS

        self.IStemplate = IStemplate

        if self.IStemplate == 0:
            prs = Presentation() 
        else:
            prs = Presentation(self.template)
            self.block_width = Inches(9.6)                    

        slide_layout = prs.slide_layouts[self.IStemplate]
        title = presentation_spec.title
        closing_title = presentation_spec.closing_title
            
        if self.IStemplate == 1:
            slide = prs.slides[0]
            PowerPointRenderer.render_titleBlock(self, slide)
        else:
            self.text_fill = RGBColor(0, 0, 0)
            slide = prs.slides.add_slide(slide_layout)
       
        PowerPointRenderer.render_title(self, slide, title)
        

        for slide in presentation_spec.slides:

            self.i += 1

            slide = prs.slides.add_slide(slide_layout)
            title = presentation_spec.slides[self.i].title

            if self.IStemplate == 1:
                PowerPointRenderer.render_titleBlock(self, slide)
                PowerPointRenderer.render_bodyBlock(self, slide)

            PowerPointRenderer.render_title(self, slide, title)
            PowerPointRenderer.render_callouts(self, slide, presentation_spec.slides)
            PowerPointRenderer.render_bullets(self, slide, presentation_spec.slides)
            PowerPointRenderer.render_images(self, slide, presentation_spec.slides)

        slide = prs.slides.add_slide(slide_layout)
        if self.IStemplate == 1:
            PowerPointRenderer.render_closingBlock(self, slide)
        PowerPointRenderer.render_closing(self, slide, closing_title)
        return prs

        
