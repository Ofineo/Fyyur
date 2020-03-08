'use strict'


$('#delete-venue').click((e)=>{
    e.preventDefault();
    const name = $('#delete-venue').attr('name')
    fetch(`/venues/${name}`,{
        method:'DELETE',
        redirect: 'follow'
    })
    .then(()=>window.location.href = "http://localhost:5000/venues")
})