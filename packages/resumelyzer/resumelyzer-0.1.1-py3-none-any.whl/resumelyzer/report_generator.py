# report_generator.py
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import base64
from openai import OpenAI

class ReportGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_pdf_report(self, analysis_result: dict, user_id: str) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        # Add watermark for free tier
        pdf.set_font('Arial', 'B', 50)
        pdf.set_text_color(220, 220, 220)
        pdf.rotate(45, x=80, y=60)
        pdf.text(60, 40, "SAMPLE - UPGRADE FOR FULL REPORT")
        pdf.rotate(0)
        
        # Add content
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Your Personality Analysis", ln=1)
        
        # Add chart
        self._add_trait_chart(pdf, analysis_result)
        
        # Add career suggestions
        suggestions = self._get_career_suggestions(analysis_result)
        pdf.multi_cell(0, 10, f"Career Suggestions:\n{suggestions}")
        
        # Add referral note
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, f"Referral ID: {user_id} - Get 1 month free for every 3 recruiters you refer!", ln=1)
        
        return pdf.output(dest='S').encode('latin1')
    
    def _add_trait_chart(self, pdf, analysis_result):
        traits = ['Openness', 'Conscientiousness', 'Extroversion', 'Agreeableness', 'Neuroticism']
        values = [analysis_result[t.lower()] for t in traits]
        
        plt.figure(figsize=(6, 3))
        plt.bar(traits, values)
        plt.ylim(0, 1)
        plt.title('Big Five Personality Traits')
        
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close()
        img_bytes.seek(0)
        
        pdf.image(img_bytes, x=10, y=40, w=180)
    
    def _get_career_suggestions(self, analysis_result):
        prompt = f"""Based on these personality traits:
        {analysis_result}
        Suggest 3-5 career paths that would be a good fit, with brief explanations.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content