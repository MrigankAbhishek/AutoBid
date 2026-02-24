export const ACTIONS = {
  PLACE_BID: 'PLACE_BID',
  SET_ITEMS: 'SET_ITEMS', 
  ADD_CAR: 'ADD_CAR'
};

export default function auctionReducer(state, action) {
  switch (action.type) {
    case ACTIONS.PLACE_BID:
      return state.map(item => {
        if (item.id === action.payload.id) {
          return { ...item, currentBid: item.currentBid + 10 };
        }
        return item;
      });

    case ACTIONS.TICK_TIMER:
      return state.map(item => {
        return item; 
      });
    
    case ACTIONS.ADD_CAR:
      return [action.payload.car, ...state];

    default:
      return state;
  }
}
