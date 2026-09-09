import { CardType } from '../types';

export type RootStackParamList = {
  Auth: undefined;
  BranchSelect: undefined;
  Home: undefined;
  Semester: undefined;
  Subject: { semester: number };
  TopicList: { subjectId: string; subjectName: string };
  Swipe: { topicId: string; topicTitle: string };
  Content: { topicId: string; topicTitle: string; mode: CardType };
};
