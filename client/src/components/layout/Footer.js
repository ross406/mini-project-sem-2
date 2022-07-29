import React from 'react';

export default function Footer() {
  return (
    // <div style={{display:"flex",flexDirection:"column",justifyContent:"flex-end"}}>
    <footer style={{position:"relative", bottom:"0", width:"100%",marginTop:"50px",padding:"30px",height:"80px"}} 
    className="bg-dark text-white text-center">
      Copyright &copy; {new Date().getFullYear()} Developer Connector
    </footer>
    // </div>
  );
}
