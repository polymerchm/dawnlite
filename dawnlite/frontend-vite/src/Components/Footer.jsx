import {
        AppBar, 
        Toolbar,
        Button, 
        Box
} from '@mui/material'

import LightModeIcon from '@mui/icons-material/LightModeTwoTone'
import EventIcon from '@mui/icons-material/EventTwoTone';
import { useNavigate } from 'react-router';

const Footer = () => {
    const navigate = useNavigate()

    return(
        <AppBar   aria-label="footer buttons"  sx={{top: 'auto', bottom:0}}>
            <Toolbar>
                <Box display='flex' flexGrow={1}>
                <Button color="inherit"
                    startIcon = {<LightModeIcon/>} 
                    onClick={() => 
                        navigate('/light')
                    }
                    >Light
                </Button>
                </Box>
                <Button color="inherit"
                    endIcon={<EventIcon/>} 
                    onClick={() => 
                        navigate('/alarm')
                    }>Alarm
                </Button>
        </Toolbar>
       </AppBar>
    )
}

export default Footer;