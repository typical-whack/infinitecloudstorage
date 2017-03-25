import $ from 'jquery';

function getFiles(success, error) {
    $.ajax({
        url: '/get_all',
        method: 'GET',
        success: success,
        error: error
    });
}

function deleteFile(id, success, error) {
    $.ajax({
        url: '/delete_file',
        method: 'POST',
        data: {
            id: id
        },
        success: success,
        error: error
    });
}

function getFile(id, success, error) {
    $.ajax({
        url: '/get_file',
        method: 'POST',
        data: {
            id: id
        },
        success: success,
        error: error
    });
}

export default {
    deleteFile,
    getFile,
    getFiles
};
