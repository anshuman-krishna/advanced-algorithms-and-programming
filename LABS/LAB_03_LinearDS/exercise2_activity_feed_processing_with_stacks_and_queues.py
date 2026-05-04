class ActivityStack:

    def __init__(self):
        self.stack = []

    def push(self, activity):
        self.stack.append(activity)
        print("Activity added:", activity)

    def pop(self):
        if not self.stack:
            print("Stack Empty")
            return
        print("Removed:", self.stack.pop())

    def peek(self):
        if not self.stack:
            print("Stack Empty")
        else:
            print("Top element:", self.stack[-1])

    def display_recent(self):
        if not self.stack:
            print("No activities")
        else:
            print("Recent Activities:")
            for act in reversed(self.stack):
                print(act)

class NotificationQueue:

    def __init__(self):
        self.queue = []

    def enqueue(self, notification):
        self.queue.append(notification)
        print("Notification added")

    def dequeue(self):
        if not self.queue:
            print("Queue Empty")
            return None
        n = self.queue.pop(0)
        print("Removed:", n)
        return n

    def priority_enqueue(self, notification):
        self.queue.insert(0, notification)
        print("Priority notification added")

    def display_pending(self):
        if not self.queue:
            print("No notifications")
        else:
            print("Pending Notifications:")
            for n in self.queue:
                print(n)

class FeedProcessor:

    def __init__(self):
        self.recent_stack = ActivityStack()
        self.notification_queue = NotificationQueue()
        self.processed_log = []
        
    def process_notification(self):
        notification = self.notification_queue.dequeue()
        if notification:
            self.recent_stack.push(notification)
            print("Processed:", notification)

    def batch_process(self, k):
        for i in range(k):
            notification = self.notification_queue.dequeue()
            if notification is None:
                break
            self.recent_stack.push(notification)
            print("Processed:", notification)
            
    def clear_history(self):
        while self.recent_stack.stack:
            activity = self.recent_stack.stack.pop()
            self.processed_log.append(activity)
        print("History moved to processed log")
        
    def get_stats(self):
        print("Recent activities:", len(self.recent_stack.stack))
        print("Pending notifications:", len(self.notification_queue.queue))
        print("Processed log:", len(self.processed_log))
        
system = FeedProcessor()
while True:
    print("\n------ Feed System Menu ------")
    print("1. Add Activity (Push)")
    print("2. Remove Activity (Pop)")
    print("3. View Top Activity (Peek)")
    print("4. Add Notification (Enqueue)")
    print("5. Add Priority Notification")
    print("6. Process Notification")
    print("7. Batch Process Notifications")
    print("8. Show Recent Activities")
    print("9. Show Pending Notifications")
    print("10. Clear History")
    print("11. Show Stats")
    print("12. Exit")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        activity = input("Enter activity: ")
        system.recent_stack.push(activity)

    elif choice == 2:
        system.recent_stack.pop()

    elif choice == 3:
        system.recent_stack.peek()

    elif choice == 4:
        notification = input("Enter notification: ")
        system.notification_queue.enqueue(notification)

    elif choice == 5:
        notification = input("Enter urgent notification: ")
        system.notification_queue.priority_enqueue(notification)

    elif choice == 6:
        system.process_notification()

    elif choice == 7:
        k = int(input("How many notifications to process: "))
        system.batch_process(k)

    elif choice == 8:
        system.recent_stack.display_recent()

    elif choice == 9:
        system.notification_queue.display_pending()

    elif choice == 10:
        system.clear_history()

    elif choice == 11:
        system.get_stats()

    elif choice == 12:
        print("Exiting...")
        break

    else:
        print("Invalid choice")