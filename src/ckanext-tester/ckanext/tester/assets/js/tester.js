"use strict";

ckan.module('tester_popover',function($){
    return{
        initialize: function () {
            $.proxyAll(this, /_on/);
            this.el.popover({title: this.options.title, html: true,
                 content: 'Loading...', placement: 'left', trigger: 'manual'});
            this.el.on('click', this._onClick);
          },
            
            snippetReceived: false,

            _onClick: function(event) {
                if (!this.snippetReceived) {
                    this.sandbox.client.getTemplate('tester_popover.html',
                                                    this.options,
                                                    this._onReceiveSnippet);
                    this.snippetReceived = true;
                }
            },
            
            _onReceiveSnippet: function(html) {
                this.el.popover('destroy');
                this.el.popover({title: this.options.title, html: true,
                                 content: html, placement: 'left'});
                this.el.popover('show');
              },
    };
});
