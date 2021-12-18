import React from 'react'
// import Fragment from 'react'
import {AppBar, 
        Toolbar,
        Typography, 
        IconButton,
        Box
} from '@mui/material'
import RecycleIcon from '@mui/icons-material/Refresh'
//import { styled } from '@mui/system';

const Header = () => {
    return (
        <div>
            <AppBar position="static">
             
                <Toolbar>
                    <Box display='flex' flexGrow={1}>
                        <Typography variant="h6" component="div" 
                        >Dawnlight</Typography>
                    </Box>
                    <IconButton 
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="refresh alarms"
                        sx={{ mr: 2 }}
                    > <RecycleIcon/>
                    </IconButton>
            
                </Toolbar>
            </AppBar>

        </div>
        )
    }

export default Header
