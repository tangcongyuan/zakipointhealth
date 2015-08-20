!function( $ ) {
    'use strict';
    $(document).ready(function() {

      /*jshint multistr: true */

        if ($('.alert').length) {
            $('.alert').each( function() {
                var growlmsg = $( this ).text();
                var growltype = 'info';

                if ($(this).hasClass('alert-debug')) {
                    growltype = 'info';
                }

                if ($(this).hasClass('alert-info')) {
                    growltype = 'info';
                }

                if ($(this).hasClass('alert-success')) {
                    growltype = 'success';
                }

                if ($(this).hasClass('alert-warning')) {
                    growltype = 'warning';
                }

                if ($(this).hasClass('alert-error')) {
                    growltype = 'danger';
                }

                if ($(this).hasClass('alert-danger')) {
                    growltype = 'danger';
                }

                $.growl({
                    message: growlmsg
                },
                {
                    animate: {
                        enter: 'animated fadeInRight',
                        exit: 'animated fadeOutRight'
                    },
                    type: growltype,
                    delay: 20000,    // 20 seconds. i think
                    template: '<div data-growl="container" class="alert" role="alert"> \
                      <button type="button" class="close" data-growl="dismiss"> \
                        <span aria-hidden="true"> &nbsp; &nbsp; x </span> \
                        <span class="sr-only">Close</span> \
                      </button> \
                      <span data-growl="icon"></span> \
                      <span data-growl="title"></span> \
                      <span style="padding-right:20px;" data-growl="message"></span> \
                      <a href="#" data-growl="url"></a> \
                    </div>'
                }
                );

            });

        }

    });
}( window.jQuery )
