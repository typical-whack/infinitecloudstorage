import $ from 'jquery';

const Links = {
    uploadFile: '/upload_file'
};

function uploadFile(file, success, error) {
    console.log('preupload');
    const data = {
        file: file
    };
    $.ajax({
        url: Links.uploadFile,
        method: 'POST',
        data: data,
        success: success,
        error: error
    });
}

export default{
    uploadFile
};
