"use-strict";

ckan.module('home_search_action', function($){
    return{
        initialize:function(){
            let search_input = this.el  // jQuery
            $.proxyAll(this,/_on/);
            search_input.on("keypress", this._onSubmit);
            $(".account-masthead").hide() 
            $(".navbar").hide() 
        },
        _onSubmit:function(e){
            if(e.which == "13"){
                sessionStorage.setItem("search_query_string", this.el.get(0).value);
                window.location.href = window.location.href + "dataset"
            }
        }
    }
})


ckan.module("search_from_home_query", function($){
    /*
        this module is used in the search.html
        with an hidden div
    */

    return{
        initialize:function(){
            let search_query_from_home_input = sessionStorage.getItem("search_query_string")
            console.log(search_query_from_home_input)
            sessionStorage.removeItem("search_query_string");
            if (search_query_from_home_input !=null && search_query_from_home_input!=""){
                $("#field-giant-search").val(search_query_from_home_input)
                $(".btn-lg").click()
            }
        }
    }
})