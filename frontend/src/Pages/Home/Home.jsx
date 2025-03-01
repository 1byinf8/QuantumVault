import Navbar from '../../Components/Navbar/Navbar';
import Footer from "../../Components/Footer/Footer";
import Hero from "../../Components/Hero/Hero"
import  "./Home.css"
function Home() {
    return (
      <div className="home">
        <Navbar/>
        <Hero/>
        <Footer/>
      </div>
    );
  }
  
  export default Home;
  