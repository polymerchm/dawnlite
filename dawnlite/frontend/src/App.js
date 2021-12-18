
import './App.css'

import Header from './Components/Header'
import Light from './Components/Light'
import Alarm from './Components/Alarm'
import Footer from './Components/Footer'

// eslint-disable-next-line
import { Routes, Route, Link}  from "react-router-dom";
import { Stack, 
// 
//   Paper 
} from '@mui/material'

// import { styled } from '@mui/material/styles';

// const Item = styled(Paper)(({ theme }) => ({
//   ...theme.typography.body2,
//   padding: theme.spacing(1),
//   textAlign: 'center',
//   color: theme.palette.text.secondary,
// }));

function App() {

  
  return (
    <div className="App">
      <Stack direction="column"
          spacing={{sx:2, sm: 3, md:5}}
      >
          <Header/>
          <Routes>
            <Route exact path="/" element={<Light/>} />
            <Route path="/light" element={<Light/>}  />
            <Route path="/alarm" element={<Alarm/>} />
          </Routes>
          <Footer/>
      </Stack>
  
    </div>
  )
}

export default App;
