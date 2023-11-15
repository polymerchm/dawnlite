import React from 'react'
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });




const InvalidAlarmEntry = ({open, setOpen, overlapTime}) => {
    //const postCloseAction = props.postCloseAction

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
          return;
        }
    
        setOpen(false);
        //postCloseAction()
    }

    return (
        <Snackbar open={open} autoHideDuration={6000} onClose={handleClose} anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}>
          <Alert onClose={handleClose} severity="error">Overlaps {overlapTime} alarm</Alert>
        </Snackbar>
    )

}

export default InvalidAlarmEntry