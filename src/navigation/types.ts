export type RootStackParamList = {
  Auth: undefined;
  BranchSelect: undefined;
  Home: undefined; // Semesters
  Subject: { semesterId: number };
  TopicList: { subjectId: number };
  Swipe: { subjectId: number };
  Content: { topicId: number };
};
