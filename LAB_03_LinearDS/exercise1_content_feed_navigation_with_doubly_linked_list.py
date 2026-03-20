class StoryNode:
    def __init__(self, story_id, user_id, content_preview, timestamp):
        self.story_id = story_id
        self.user_id = user_id
        self.content_preview = content_preview
        self.timestamp = timestamp
        self.views = 0
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    def add_story(self, node):
        node.next = None
        node.views = 0
        if self.head is None:
            node.prev = None
            self.head = node
            self.tail = node
            self.current = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1

    def remove_story(self, story_id):
        temp = self.head
        while temp is not None:
            if temp.story_id == story_id:
                if temp.prev is not None:
                    temp.prev.next = temp.next
                else:
                    self.head = temp.next
                
                if temp.next is not None:
                    temp.next.prev = temp.prev
                else:
                    self.tail = temp.prev
                
                if self.current == temp:
                    self.current = temp.next
                
                self.size -= 1
                break
            temp = temp.next

    def move_forward(self):
        if self.current is not None and self.current.next is not None:
            self.current = self.current.next
            return self.current.content_preview
        return "End of feed"

    def move_backward(self):
        if self.current is not None and self.current.prev is not None:
            self.current = self.current.prev
            return self.current.content_preview
        return "Beginning of feed"

    def jump_to(self, story_id):
        temp = self.head
        while temp is not None:
            if temp.story_id == story_id:
                self.current = temp
                break
            temp = temp.next

    def insert_after(self, current_id, new_story):
        temp = self.head
        while temp is not None:
            if temp.story_id == current_id:
                new_story.next = temp.next
                new_story.prev = temp
                
                if temp.next is not None:
                    temp.next.prev = new_story
                else:
                    self.tail = new_story
                
                temp.next = new_story
                self.size += 1
                break
            temp = temp.next

    def display_around_current(self, k):
        results = []
        temp = self.current
        
        count = 0
        while temp is not None and count < k:
            temp = temp.prev
            count += 1
        
        if temp is None:
            temp = self.head
        
        total_to_show = (k * 2) + 1
        count = 0
        while temp is not None and count < total_to_show:
            results.append(temp.content_preview)
            temp = temp.next
            count += 1
        
        return results

    def track_view(self):
        if self.current is not None:
            self.current.views += 1

    def most_viewed(self):
        if self.head is None:
            return None
        
        max_node = self.head
        temp = self.head.next
        
        while temp is not None:
            if temp.views > max_node.views:
                max_node = temp
            temp = temp.next
        
        return max_node

    def reorder_by_views(self):
        if self.head is None or self.head.next is None:
            return
        
        swapped = True
        while swapped:
            swapped = False
            current_node = self.head
            
            while current_node.next is not None:
                next_node = current_node.next
                if current_node.views < next_node.views:
                    current_node.views, next_node.views = next_node.views, current_node.views
                    current_node.story_id, next_node.story_id = next_node.story_id, current_node.story_id
                    current_node.content_preview, next_node.content_preview = next_node.content_preview, current_node.content_preview
                    
                    swapped = True
                current_node = current_node.next


# verification
if __name__ == "__main__":
    feed = DoublyLinkedList()
    
    feed.add_story(StoryNode("1", "userA", "Trip to Paris", 1000))
    feed.add_story(StoryNode("2", "userB", "My new puppy", 1005))
    feed.add_story(StoryNode("3", "userC", "Cooking pasta", 1010))
    
    print("Initial Feed added. Current story:")
    print(feed.current.content_preview if feed.current else "None")
    
    print("\nMoving Forward:")
    print(feed.move_forward())
    
    print("\nTracking views for the puppy story...")
    feed.track_view()
    feed.track_view()
    feed.track_view()
    
    print("\nJumping back to Paris story and adding views...")
    feed.jump_to("1")
    feed.track_view()
    
    print("\nMost viewed story right now:")
    best = feed.most_viewed()
    print(f"{best.content_preview} with {best.views} views")
    
    print("\nInserting a breaking news story after Paris...")
    feed.insert_after("1", StoryNode("4", "userD", "Breaking: Snow in May", 1015))
    
    print("\nReordering feed by views...")
    feed.reorder_by_views()
    
    print("\nFinal feed order (highest views first):")
    temp = feed.head
    while temp is not None:
        print(f"* {temp.content_preview} ({temp.views} views)")
        temp = temp.next