/* Javascript for GPTeacherXBlock. */

function GPTeacherXBlock(runtime, element, init_args) {

    var handlerUrl = runtime.handlerUrl(element, 'get_response');

  $(function() {
    var chatHistory = $('.chat-history', element);
    var sendButton = $('.send-button', element);
    var userInput = $('.user-input', element);
  
    function getResponse() {
      var text = userInput.val();
      chatHistory.append('<div class="chat-message user-message"><p>' + text + '</p></div>');
      $.ajax({
        url: handlerUrl,
        method: "POST",
        data: JSON.stringify({ 'user_input': text }),
        success: function(response) {
          chatHistory.append('<div class="chat-message gpt-message"><p>' + response.response + '</p></div>');
          userInput.val('');
        },
        error: function(jqXHR, textStatus, errorThrown) {
          chatHistory.append('<div class="chat-message gpt-message"><p>' + errorThrown + '</p></div>');
        }
      });
    }
  
    sendButton.click(getResponse);

  });
}
