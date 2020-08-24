const BASE_URL = 'https://localhost:5000/private-notes'


function delete_note(data) {
    let item_id = data.getAttribute("data-id");
    fetch(BASE_URL + '/delete/' + item_id, {
        method: 'DELETE',
        credentials: 'include'
    })
        .then(response => response.json())
        .then(result => location.reload())
        .catch(err => console.log(err))
}


function delete_file(data) {
    let item_id = data.getAttribute("data-id");
    fetch(BASE_URL + '/files/delete/' + item_id, {
        method: 'DELETE',
        credentials: 'include'
    })
        .then(response => response.json())
        .then(result => location.reload())
        .catch(err => console.log(err))
}

function upload_file(data) {
    let fileData = new FormData();
    let file = data.files[0];
    let item_id = data.getAttribute("id");
    fileData.append("Note", file)
    console.log(item_id);
    console.log(file);
    fetch(BASE_URL + '/files/' + item_id, {
        method: 'PATCH',
        credentials: 'include',
        body: fileData
    })
        .then(response => response.json())
        .then(data => location.reload())
        .catch(err => console.log(err))
}


