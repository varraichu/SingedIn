import RichTextRenderer from "@/components/RichTextRenderer";
import LandingPage from "./components/LandingPage";

const sampleText = `
I was *working on the weekend* (yes, and?) like usual, grinding away at my desk while everyone else seemed to be out enjoying the sun. Deadlines stacked up, and I kept reminding myself *started from the bottom now we here* (positions), but it didn't feel like I'd reached anywhere yet. Coffee cups piled high, and still *I can't feel my face when I'm with you* (Crash) echoed through my headphones, giving me just enough energy to keep pushing through.
By the time the evening rolled around, I thought about stepping away, *but I'm still standing, yeah yeah yeah* (Ashley) was playing, and somehow it kept me glued to the chair. I remembered the nights when *we found love in a hopeless place* (We Found Love) and how much those memories fueled me when things got tough. I told myself I will survive, oh, as long as I know *how to love I know I'll stay alive* (I Will Always Love You), and suddenly the exhaustion didn't seem as heavy.
Finally, as the clock struck midnight, I leaned back and laughed — *it's a hard knock life for us* (Midnight Rain) but maybe that's the beauty of it. My friends texted me, telling me to come out, and I thought of *how we're all just kids in America* (Hopeless), trying to figure it out one day at a time. I shut my laptop, grabbed my jacket, and whispered to myself *tonight's gonna be a good night* (Call Me Maybe), ready to trade work stress for music, laughter, and maybe a little freedom.

I was *working on the weekend* (yes, and?) like usual, grinding away at my desk while everyone else seemed to be out enjoying the sun. Deadlines stacked up, and I kept reminding myself *started from the bottom now we here* (positions), but it didn't feel like I'd reached anywhere yet. Coffee cups piled high, and still *I can't feel my face when I'm with you* (Crash) echoed through my headphones, giving me just enough energy to keep pushing through.
By the time the evening rolled around, I thought about stepping away, *but I'm still standing, yeah yeah yeah* (Ashley) was playing, and somehow it kept me glued to the chair. I remembered the nights when *we found love in a hopeless place* (We Found Love) and how much those memories fueled me when things got tough. I told myself I will survive, oh, as long as I know *how to love I know I'll stay alive* (I Will Always Love You), and suddenly the exhaustion didn't seem as heavy.
Finally, as the clock struck midnight, I leaned back and laughed — *it's a hard knock life for us* (Midnight Rain) but maybe that's the beauty of it. My friends texted me, telling me to come out, and I thought of *how we're all just kids in America* (Hopeless), trying to figure it out one day at a time. I shut my laptop, grabbed my jacket, and whispered to myself *tonight's gonna be a good night* (Call Me Maybe), ready to trade work stress for music, laughter, and maybe a little freedom.
`;

// const sampleText = `
// I was *working on the weekend like usual* (positions)... then *Don't Want You* (Don't Want You) came on.
// `;

export default function App() {
  return (
    <div className="bg-background"> 
    <LandingPage></LandingPage>
    </div>
  );
}
