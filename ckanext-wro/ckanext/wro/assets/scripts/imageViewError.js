ckan.module("image_view_error_handler",function($){
    return{
        initialize:function(){
            console.log("error handler init")
                $.proxyAll(this,/_on/); 
                this.el.on('error', this._handleError)
            },
        _handleError:function(e){
                console.log("this didn't load!")
        },
    }
    
})