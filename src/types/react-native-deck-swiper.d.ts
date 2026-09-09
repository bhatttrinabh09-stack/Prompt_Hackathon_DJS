declare module 'react-native-deck-swiper' {
  import { Component } from 'react';
  import { StyleProp, ViewStyle } from 'react-native';

  export interface SwiperProps<T> {
    cards: T[];
    renderCard: (card: T, index: number) => JSX.Element;
    onSwiped?: (cardIndex: number) => void;
    onSwipedLeft?: (cardIndex: number) => void;
    onSwipedRight?: (cardIndex: number) => void;
    onSwipedTop?: (cardIndex: number) => void;
    onSwipedBottom?: (cardIndex: number) => void;
    onSwipedAll?: () => void;
    cardIndex?: number;
    backgroundColor?: string;
    stackSize?: number;
    stackSeparation?: number;
    overlayLabels?: any;
    animateOverlayLabelsOpacity?: boolean;
    animateCardOpacity?: boolean;
    useViewOverflow?: boolean;
    disableTopSwipe?: boolean;
    disableBottomSwipe?: boolean;
    disableLeftSwipe?: boolean;
    disableRightSwipe?: boolean;
    cardStyle?: StyleProp<ViewStyle>;
    containerStyle?: StyleProp<ViewStyle>;
  }

  export default class Swiper<T> extends Component<SwiperProps<T>> {
    swipeLeft: () => void;
    swipeRight: () => void;
    swipeTop: () => void;
    swipeBottom: () => void;
    jumpToCardIndex: (cardIndex: number) => void;
  }
}
