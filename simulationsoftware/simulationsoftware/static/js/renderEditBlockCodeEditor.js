function get_edit_block_code_editor_ui(ev){
    const block_id = document.getElementById(ev).value;
    if(block_id){
        fetch(`${block_id}/get_edit_block_code_editor_ui`,{
            method:'GET',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    window.location = data['edit_code_editor_ui_url'];
                }
            })
        .catch(error => console.log("Error",error));
    }
    else{
        alert("please select a logic to edit code");
    }
}

function getCSRFToken(){
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}