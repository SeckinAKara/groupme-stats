library(ggplot2)

entire_log <- read.csv('groupme_logs.csv', header = FALSE)

messages <- data.frame('person' = entire_log$V1, 'date' = entire_log$V2, 'message' = entire_log$V3)

all_names <- data.frame('person' = levels(messages$person), 'count' = c(0))


graph_word <- function(word) {
  messages_with_word <- messages[grepl(word,messages$message),]
  for(row in 1:length(messages_with_word$person)) {
    all_names[all_names$person == messages_with_word$person[row],]$count <- all_names[all_names$person == messages_with_word$person[row],]$count + 1
    
  }
  
  all_names$person <- factor(all_names$person, levels = all_names$person[order(-all_names$count)])
  
  to_graph <- data.frame('person' = levels(all_names$person)[1:10], 'count' = all_names$count[order(-all_names$count)][1:10])
  
  to_graph$person <- factor(to_graph$person, levels = to_graph$person[order(-to_graph$count)])
  
  graphed <- ggplot(data = to_graph, aes(x = person, y = count)) + geom_bar(stat = 'identity') + labs(title = word)
  print(graphed)
  
}