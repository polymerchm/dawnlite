import React from 'react'
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import { ACTIONS } from '../App'


const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });



const InvalidAlarmEntry = ({alert, dispatch}) => {
    //const postCloseAction = props.postCloseAction

  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    } else {
      dispatch({ action: ACTIONS.SET_ALERT, payload: { show: false, type: null, value: null } })
    }
        //postCloseAction()
    }

    const alertToDisplay = () => {
      if (alert.show === null) {
        return null
      }
      switch (alert.type) {
        case 'nodays':
          return (<Alert onClose={handleClose} severity="error">Set at least on day</Alert>)
        case 'overlap':
          return (<Alert onClose={handleClose} severity="error">Overlaps {alert.value} alarm</Alert>)
        default:
          return (<Alert onClose={handleClose} severity="error">Invalid alert type </Alert>)
      }
    }
    

    return (
        <Snackbar open={alert.show} autoHideDuration={6000} onClose={handleClose} anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}>
          {alertToDisplay()}
        </Snackbar>
    )

}

export default InvalidAlarmEntry